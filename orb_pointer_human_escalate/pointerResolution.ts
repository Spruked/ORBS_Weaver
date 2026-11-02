/**
 * Package B — target resolution chain.
 *
 * Implements Section 4, steps 2–4 of the doctrine: confidence floor,
 * the four-tier resolution chain, and the map_recovering fallback.
 *
 * TODO(integration): replace the four `try*` function bodies with
 * your actual DOM/accessibility querying. Signatures and control
 * flow are the part that matters — they encode the doctrine's
 * ordering and stop-at-first-success rule.
 */

import type { PlotRecord } from "./pointerPlotTypes";

export interface ResolvedTarget {
  element: Element;
  method: "semantic_locator" | "content_fingerprint" | "accessibility_role" | "visual_verification";
  onScreen: boolean;
}

export interface ResolutionResult {
  status: "resolved" | "unresolved" | "below_confidence";
  target?: ResolvedTarget;
  /** Only set when status === "resolved" via a fallback tier that
   *  didn't match the record's stored semantic_locator — signals the
   *  caller should emit a CandidateCorrection. */
  divergedFromStoredLocator?: boolean;
}

// Minimum scan-time confidence required before attempting resolution
// at all. Below this, the ORB answers verbally and never tries to point.
export const CONFIDENCE_FLOOR = 0.55;

export async function resolveTarget(record: PlotRecord): Promise<ResolutionResult> {
  if (record.confidence < CONFIDENCE_FLOOR) {
    return { status: "below_confidence" };
  }

  // Tier 1: semantic_locator (the stored, presumed-current locator)
  const bySemanticLocator = trySemanticLocator(record.semantic_locator);
  if (bySemanticLocator) {
    return {
      status: "resolved",
      target: { element: bySemanticLocator, method: "semantic_locator", onScreen: isOnScreen(bySemanticLocator) },
    };
  }

  // Tier 2: content fingerprint match within the current page
  const byFingerprint = tryContentFingerprint(record.content_fingerprint);
  if (byFingerprint) {
    return {
      status: "resolved",
      target: { element: byFingerprint, method: "content_fingerprint", onScreen: isOnScreen(byFingerprint) },
      divergedFromStoredLocator: true,
    };
  }

  // Tier 3: accessibility/role-based locator, using target_type + meaning as hints
  const byRole = tryAccessibilityRole(record);
  if (byRole) {
    return {
      status: "resolved",
      target: { element: byRole, method: "accessibility_role", onScreen: isOnScreen(byRole) },
      divergedFromStoredLocator: true,
    };
  }

  // Tier 4: localized visual verification (Tesseract-style), current page/section ONLY
  const byVisual = await tryVisualVerification(record);
  if (byVisual) {
    return {
      status: "resolved",
      target: { element: byVisual, method: "visual_verification", onScreen: isOnScreen(byVisual) },
      divergedFromStoredLocator: true,
    };
  }

  return { status: "unresolved" };
}

function trySemanticLocator(locator: string): Element | null {
  try {
    return document.querySelector(locator) || document.querySelector(`[data-orb-target="${cssEscape(locator)}"]`);
  } catch {
    return null;
  }
}

function tryContentFingerprint(fingerprint: string): Element | null {
  const normalizedFingerprint = normalizeText(fingerprint);
  if (!normalizedFingerprint) return null;

  return bestVisibleElement((element) => {
    const text = normalizeText(element.textContent || "");
    if (!text) return 0;
    if (text.includes(normalizedFingerprint)) return 1;
    if (normalizedFingerprint.includes(text) && text.length > 24) return 0.78;
    return tokenOverlapScore(text, normalizedFingerprint);
  });
}

function tryAccessibilityRole(record: PlotRecord): Element | null {
  const expected = normalizeText([record.meaning, ...record.intent_aliases].join(" "));
  const roleHints = roleHintsForTarget(record.target_type);
  return bestVisibleElement((element) => {
    const role = element.getAttribute("role") || element.tagName.toLowerCase();
    if (roleHints.length > 0 && !roleHints.includes(role)) return 0;
    const accessibleName = normalizeText(
      [
        element.getAttribute("aria-label"),
        element.getAttribute("title"),
        element.textContent,
      ].filter(Boolean).join(" "),
    );
    return tokenOverlapScore(accessibleName, expected);
  });
}

async function tryVisualVerification(record: PlotRecord): Promise<Element | null> {
  const expected = normalizeText([record.meaning, record.content_fingerprint, ...record.intent_aliases].join(" "));
  return bestVisibleElement((element) => {
    if (!isOnScreen(element)) return 0;
    const targetId = normalizeText(element.getAttribute("data-orb-target") || "");
    const label = normalizeText(
      [
        element.getAttribute("aria-label"),
        element.getAttribute("title"),
        element.textContent,
      ].filter(Boolean).join(" "),
    );
    return Math.max(tokenOverlapScore(targetId, expected), tokenOverlapScore(label, expected));
  });
}

function isOnScreen(element: Element): boolean {
  const rect = element.getBoundingClientRect();
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
  const viewportWidth = window.innerWidth || document.documentElement.clientWidth;
  return rect.bottom >= 0 && rect.right >= 0 && rect.top <= viewportHeight && rect.left <= viewportWidth;
}

function bestVisibleElement(score: (element: Element) => number): Element | null {
  let best: { element: Element; score: number } | null = null;
  const candidates = Array.from(document.querySelectorAll("a, button, input, select, textarea, section, article, [role], [data-orb-target], [aria-label], [title]"));
  for (const element of candidates) {
    const rect = element.getBoundingClientRect();
    if (rect.width < 4 || rect.height < 4) continue;
    const nextScore = score(element);
    if (nextScore > 0.42 && (!best || nextScore > best.score)) {
      best = { element, score: nextScore };
    }
  }
  return best?.element || null;
}

function normalizeText(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9.\s-]/g, " ").replace(/\s+/g, " ").trim();
}

function tokenOverlapScore(value: string, expected: string): number {
  const valueTokens = new Set(normalizeText(value).split(" ").filter((token) => token.length > 2));
  const expectedTokens = normalizeText(expected).split(" ").filter((token) => token.length > 2);
  if (!valueTokens.size || !expectedTokens.length) return 0;
  const hits = expectedTokens.filter((token) => valueTokens.has(token)).length;
  return hits / expectedTokens.length;
}

function roleHintsForTarget(targetType: PlotRecord["target_type"]): string[] {
  if (targetType === "nav") return ["a", "nav", "link"];
  if (targetType === "button" || targetType === "download") return ["button", "a", "link"];
  if (targetType === "form_field") return ["input", "textarea", "select", "textbox", "combobox"];
  if (targetType === "heading") return ["h1", "h2", "h3", "h4", "h5", "h6", "heading"];
  if (targetType === "section" || targetType === "price_card") return ["section", "article", "region"];
  return [];
}

function cssEscape(value: string): string {
  if ("CSS" in window && typeof window.CSS.escape === "function") return window.CSS.escape(value);
  return value.replace(/["\\]/g, "\\$&");
}
