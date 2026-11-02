import { createFileRoute } from "@tanstack/react-router";
import { ArrowDownToLine, FileCode2, Package } from "lucide-react";

export const Route = createFileRoute("/")({ component: Home });

const FILES = [
  { name: "models.py", desc: "WorldState, ActionProposal, ExecutionPermit contracts" },
  { name: "core4.py", desc: "Kant / Locke / Hume / Spinoza deterministic evaluation" },
  { name: "admission.py", desc: "Hard Admission Gate + short-lived permit issuance" },
  { name: "middleware.py", desc: "TTI validation path: Core-4 → admission → execution" },
  { name: "event_bus.py", desc: "Asynchronous execution fabric and lane queues" },
  { name: "telemetry.py", desc: "Deterministic telemetry reduction into runtime state" },
  { name: "demo.py", desc: "End-to-end permit-path demonstration" },
  { name: "__init__.py", desc: "Package exports" },
  { name: "README.md", desc: "Authority-path contract and run instructions" },
];

const DOWNLOADS = [
  {
    href: "/ral_core.zip",
    filename: "ral_core.zip",
    label: "Download permit-aware RAL Core",
  },
  {
    href: "https://github.com/Spruked/Orbot/archive/refs/heads/ral-ros-bridge-package-v2.zip",
    filename: "ral-ros-bridge-package-v2.zip",
    label: "Download ROS ↔ NATS bridge",
  },
];

function Home() {
  return (
    <main className="relative mx-auto flex min-h-screen max-w-xl flex-col justify-center px-5 py-12 sm:px-8">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-56 bg-[radial-gradient(ellipse_at_top,color-mix(in_oklab,var(--color-primary)_18%,transparent),transparent_70%)]"
      />

      <header className="relative mb-8">
        <p className="mb-3 font-mono text-xs tracking-[0.18em] text-primary uppercase">
          Verified Python runtime packages
        </p>
        <h1 className="text-3xl font-semibold tracking-tight text-fg sm:text-4xl">
          Orbot TTI / RAL Runtime
        </h1>
        <p className="mt-3 max-w-md text-[15px] leading-relaxed text-muted">
          Core-4 Tribunal, deterministic Hard Admission, short-lived Execution Permits,
          asynchronous execution lanes, and the permit-aware ROS ↔ NATS bridge.
        </p>
      </header>

      <div className="relative mb-8 grid gap-3">
        {DOWNLOADS.map((item) => (
          <a
            key={item.filename}
            href={item.href}
            download={item.filename}
            className="flex min-h-12 items-center justify-center gap-2.5 rounded-lg bg-primary px-5 py-3.5 text-[15px] font-semibold text-primary-fg transition-opacity hover:opacity-90"
          >
            <ArrowDownToLine className="size-5" strokeWidth={2} />
            {item.label}
          </a>
        ))}
      </div>

      <section className="overflow-hidden rounded-lg border border-border bg-surface">
        <div className="flex items-center gap-2 border-b border-border px-4 py-3">
          <Package className="size-4 text-primary" />
          <h2 className="text-sm font-medium">RAL Core source downloads</h2>
        </div>
        <ul>
          {FILES.map((f) => (
            <li key={f.name} className="border-b border-border last:border-0">
              <a
                href={`/ral_core/${f.name}`}
                download={f.name}
                className="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-elevated"
              >
                <FileCode2 className="size-4 shrink-0 text-muted" />
                <span className="min-w-0 flex-1">
                  <span className="block font-mono text-[13px] text-fg">{f.name}</span>
                  <span className="block text-xs text-muted">{f.desc}</span>
                </span>
              </a>
            </li>
          ))}
        </ul>
      </section>

      <p className="mt-6 font-mono text-xs leading-relaxed text-muted">
        No valid Execution Permit, no normal execution.
      </p>
    </main>
  );
}
