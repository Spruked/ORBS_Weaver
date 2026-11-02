"""Volatile attention policy for purposeful, non-obstructive Orb movement."""
from __future__ import annotations

import math
import random
import time
from .presentation import segment_hits_rect


class DesktopAttention:
    """Follow a stable active work area, patrol around it, and perch briefly."""

    APPROACH_AFTER = 8.0
    PERCH_AFTER = 90.0
    PERCH_MAX_SECONDS = 5.0
    PERCH_COOLDOWN = 180.0
    RETURN_AFTER_IDLE_MS = 300_000

    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.key = None
        self.since = 0.0
        self.rect = None
        self.phase = "ambient"
        self.perching_until = 0.0
        self.last_perch = 0.0
        self.last_laps = 0
        self.last_offer = 0.0
        self.perch_count = 0
        self.pending_offer = False
        self.offer_deadline = 0.0
        self.suppressed_until = 0.0
        self.last_update = 0.0
        self.return_sent = False
        self.result = {"phase": "ambient", "offer": False}

    @staticmethod
    def _rect(frame):
        value = frame.get("foreground_rect")
        if not isinstance(value, dict):
            return None
        keys = ("left", "top", "right", "bottom")
        if not all(isinstance(value.get(k), (int, float)) for k in keys):
            return None
        rect = tuple(float(value[k]) for k in keys)
        return rect if rect[2] > rect[0] and rect[3] > rect[1] else None

    @staticmethod
    def _work_path(frame, rect):
        monitors = frame.get("monitors") or []
        if not monitors or not rect:
            return None
        left, top, right, bottom = rect
        orb_radius = max(float(frame.get("width", 240)), float(frame.get("height", 240))) / 2
        # Leave a visible gap beyond the full native window so the rendered Orb
        # does not cover the active application or its controls.
        target_pad = orb_radius + 48.0
        clear_pad = orb_radius + 24.0
        width, height = right-left, bottom-top
        xs = [left + width*f for f in (0.0, 0.25, 0.5, 0.75, 1.0)]
        ys = [top + height*f for f in (0.0, 0.25, 0.5, 0.75, 1.0)]
        # A clockwise series of near-edge lanes creates a real patrol instead
        # of repeatedly aiming at only the four window midpoints.
        candidates = ([(x, top-target_pad) for x in xs]
                      + [(right+target_pad, y) for y in ys[1:]]
                      + [(x, bottom+target_pad) for x in reversed(xs[:-1])]
                      + [(left-target_pad, y) for y in reversed(ys[1:-1])])
        cx, cy = (left + right) / 2, (top + bottom) / 2
        # Prefer the display containing most of the foreground window.
        overlaps = []
        for index, monitor in enumerate(monitors):
            ml, mt = monitor["x"], monitor["y"]
            mr, mb = ml + monitor["width"], mt + monitor["height"]
            area = max(0, min(right, mr)-max(left, ml)) * max(0, min(bottom, mb)-max(top, mt))
            overlaps.append((area, index))
        preferred = max(overlaps)[1]
        order = [preferred] + [i for _, i in sorted(overlaps, reverse=True) if i != preferred]
        targets = []
        for x, y in candidates:
            valid = []
            for index in order:
                monitor = monitors[index]
                if (monitor["x"] + orb_radius <= x <= monitor["x"] + monitor["width"] - orb_radius
                        and monitor["y"] + orb_radius <= y <= monitor["y"] + monitor["height"] - orb_radius):
                    valid.append(index)
            if valid:
                # Stay on the app's display when the lane fits; use an adjacent
                # display only for positions that cannot fit on that display.
                index = preferred if preferred in valid else min(valid, key=lambda i: math.dist(
                    (x, y), (monitors[i]["x"]+monitors[i]["width"]/2,
                             monitors[i]["y"]+monitors[i]["height"]/2)))
                if not any(t["monitor"] == index and math.dist((x, y), (t["x"], t["y"])) < 20 for t in targets):
                    targets.append({"x": round(x), "y": round(y), "monitor": index})
        if not targets:
            return None
        if not any(target["monitor"] == preferred for target in targets):
            preferred = min((target["monitor"] for target in targets), key=lambda i: math.dist(
                (cx, cy), (monitors[i]["x"]+monitors[i]["width"]/2,
                           monitors[i]["y"]+monitors[i]["height"]/2)))
        return {"rect": rect, "clear_pad": clear_pad, "targets": targets, "monitor": preferred}

    def manual_override(self, seconds=900):
        self.suppressed_until = time.monotonic() + seconds
        self.pending_offer = False
        self.phase = "ambient"
        self.key = None

    def feedback(self, declined):
        if not self.pending_offer:
            return {"accepted": False}
        self.pending_offer = False
        self.suppressed_until = time.monotonic() + (3600 if declined else 1200)
        self.phase = "patrolling"
        return {"accepted": True, "declined": declined}

    def update(self, frame, motion, now=None):
        now = time.monotonic() if now is None else now
        if now-self.last_update < 1.0:
            self.result["offer"] = False
            self.result["return_to_dock"] = False
            return self.result
        self.last_update = now
        if self.pending_offer and now >= self.offer_deadline:
            self.pending_offer = False
            self.suppressed_until = now + 1200

        idle_ms = frame.get("idle_ms")
        voice_state = str(frame.get("voice_state") or "").casefold()
        voice_busy = voice_state in {"thinking", "speaking", "opening microphone"}
        return_to_dock = (isinstance(idle_ms, int) and idle_ms >= self.RETURN_AFTER_IDLE_MS
                          and not voice_busy and now >= self.suppressed_until)
        if return_to_dock:
            self.result = {"phase": "returning_to_dock", "offer": False, "return_to_dock": True}
            return self.result

        app = str(frame.get("foreground_app") or "")
        rect = self._rect(frame)
        if now < self.suppressed_until:
            self.result = {"phase": self.phase, "offer": False, "return_to_dock": False}
            return self.result
        if app.casefold() in {"orbot-desktop.exe", "dock-station.exe", "orbot-dock-station.exe"}:
            self.key = None
            motion.clear_work_path()
            if motion.authority in ("hold", "guided"):
                motion.set_authority("ambient")
            self.phase = "ambient"
            self.result = {"phase": self.phase, "offer": False, "return_to_dock": False}
            return self.result
        if not app or rect is None:
            self.key = None
            motion.clear_work_path()
            if motion.authority in ("hold", "guided"):
                motion.set_authority("ambient")
            self.phase = "ambient"
            self.result = {"phase": self.phase, "offer": False, "return_to_dock": False}
            return self.result

        # Stability follows the application and window geometry, not its title;
        # tab names and document titles often change during the same work session.
        key = app.casefold()
        moved = self.rect is not None and any(abs(a-b) > 40 for a, b in zip(rect, self.rect))
        if key != self.key or moved:
            self.key, self.since, self.rect = key, now, rect
            self.phase = "observing"
            self.perching_until = 0.0
            self.pending_offer = False
            if motion.authority in ("hold", "guided"):
                motion.set_authority("ambient")
        else:
            self.rect = rect

        duration = now-self.since
        work = self._work_path(frame, rect)
        if duration >= self.APPROACH_AFTER and work:
            motion.set_work_path(work["rect"], work["clear_pad"], work["targets"], work["monitor"])
            center = (frame["x"]+frame["width"]/2, frame["y"]+frame["height"]/2)
            current_monitor = motion._monitor(center, frame["monitors"])
            if current_monitor != work["monitor"] and motion.authority != "guided":
                candidates = [t for t in work["targets"] if t["monitor"] == work["monitor"]]
                clear = (rect[0]-work["clear_pad"], rect[1]-work["clear_pad"],
                         rect[2]+work["clear_pad"], rect[3]+work["clear_pad"])
                safe = [t for t in candidates if not segment_hits_rect(center, (t["x"], t["y"]), clear)]
                # If the native Orb currently overlaps the foreground window,
                # let it take the shortest route out to a clear perimeter lane.
                inside = clear[0] <= center[0] <= clear[2] and clear[1] <= center[1] <= clear[3]
                target = min(safe or (candidates if inside else []),
                             key=lambda t: math.dist(center, (t["x"], t["y"])), default=None)
                if target:
                    motion.set_authority("guided", (target["x"], target["y"]))
                    self.phase = "approaching"
            elif self.phase not in ("approaching", "observing_briefly"):
                self.phase = "patrolling"
        elif duration >= self.APPROACH_AFTER:
            # A fullscreen window on a single display may leave no safe lane.
            # Do not invent a target that would knowingly cover it.
            motion.clear_work_path()
        if self.phase == "approaching" and motion.last_result.get("state") == "guided_arrived":
            motion.set_authority("ambient")
            self.phase = "patrolling"

        # A hold is a short observation beat earned only by a completed patrol
        # lap, sustained focus, owner inactivity, and a cooldown.
        laps = motion.work_laps
        lap_completed = laps > self.last_laps
        self.last_laps = laps
        if self.perching_until and now >= self.perching_until:
            if motion.authority == "hold":
                motion.set_authority("ambient")
            self.perching_until = 0.0
            self.phase = "patrolling"
        elif self.perching_until and isinstance(idle_ms, int) and idle_ms < 3000:
            motion.set_authority("ambient")
            self.perching_until = 0.0
            self.phase = "patrolling"

        if (lap_completed and duration >= self.PERCH_AFTER and not self.perching_until
                and now-self.last_perch >= self.PERCH_COOLDOWN and isinstance(idle_ms, int)
                and 5000 <= idle_ms < self.RETURN_AFTER_IDLE_MS and self.rng.random() < 0.10):
            motion.set_authority("hold")
            self.perching_until = now + self.PERCH_MAX_SECONDS
            self.last_perch = now
            self.perch_count += 1
            self.phase = "observing_briefly"

        offer = False
        if (self.perching_until and not self.pending_offer and now-self.last_offer >= 1200
                and isinstance(idle_ms, int) and idle_ms >= 30000 and voice_state == "listening"):
            self.pending_offer = True
            self.offer_deadline = now + 180
            self.last_offer = now
            offer = True
        self.result = {"phase": self.phase, "offer": offer, "return_to_dock": False,
                       "work_monitor": work["monitor"] if work else None,
                       "perches": self.perch_count,
                       "observation": {"application": app, "window_title": str(frame.get("window_title") or "")[:240],
                                       "stable_seconds": round(duration), "idle_ms": idle_ms} if offer else None}
        return self.result
