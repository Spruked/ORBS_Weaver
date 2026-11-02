"""Volatile cancellation for conversation media; never execution permission."""
from dataclasses import dataclass, field
from threading import Event, RLock
from uuid import uuid4


class VoiceCancelled(Exception):
    pass


@dataclass
class VoiceTurn:
    session_id: str
    turn_id: str
    cancelled: Event = field(default_factory=Event)

    def check(self):
        if self.cancelled.is_set():
            raise VoiceCancelled("Voice turn cancelled")


class VoiceTurns:
    def __init__(self):
        self.lock = RLock()
        self.active = {}

    def begin(self, session_id, turn_id=None):
        turn = VoiceTurn(session_id, turn_id or str(uuid4()))
        with self.lock:
            if session_id in self.active:
                raise ValueError("A voice turn is still finishing; wait for cancellation to complete")
            self.active[session_id] = turn
        return turn

    def cancel(self, session_id, turn_id=None):
        with self.lock:
            turn = self.active.get(session_id)
            if turn is None or (turn_id and turn_id != turn.turn_id):
                return False
            turn.cancelled.set()
            return True

    def end(self, turn):
        with self.lock:
            if self.active.get(turn.session_id) is turn:
                del self.active[turn.session_id]


voice_turns = VoiceTurns()
