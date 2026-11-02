# note_binding.py

import time
from dataclasses import dataclass, field
from typing import Callable, Optional

import mido as md

Callback = Callable[["NoteBinding"], None]

ALL_SOUND_OFF = 120
ALL_NOTES_OFF = 123
_PANIC_CONTROLS = (ALL_SOUND_OFF, ALL_NOTES_OFF)


@dataclass(eq=False)
class NoteBinding:
    note: int
    channel: Optional[int] = None
    on_press: Optional[Callback] = None
    on_release: Optional[Callback] = None

    is_pressed: bool = field(default=False, init=False)
    velocity: int = field(default=0, init=False)
    release_velocity: int = field(default=0, init=False)
    pressed_at: Optional[float] = field(default=None, init=False)

    @property
    def held_time(self) -> float:
        if self.pressed_at is None:
            return 0.0
        return time.monotonic() - self.pressed_at

    # --- decorators for easy code binding  ---
    def press(self, fn: Callback) -> Callback:
        self.on_press = fn
        return fn

    def release(self, fn: Callback) -> Callback:
        self.on_release = fn
        return fn

    # --- Work with MIDI ---
    def matches(self, msg: md.Message) -> bool:
        return (
            msg.type in ("note_on", "note_off")
            and msg.note == self.note
            and (self.channel is None or msg.channel == self.channel)
        )

    def handle(self, msg: md.Message) -> bool:
        if msg.type == "control_change" and msg.control in _PANIC_CONTROLS:
            if self.channel is None or msg.channel == self.channel:
                self.reset()
            return False

        if not self.matches(msg):
            return False

        is_note_on = msg.type == "note_on" and msg.velocity > 0
        is_note_off = msg.type == "note_off" or (
                msg.type == "note_on" and msg.velocity == 0
        )

        if is_note_on and not self.is_pressed:
            self.is_pressed = True
            self.velocity = msg.velocity
            self.release_velocity = 0
            self.pressed_at = time.monotonic()
            if self.on_press:
                self.on_press(self)

        elif is_note_off and self.is_pressed:
            self._release(msg.velocity)

        return True

    def reset(self, notify: bool = True) -> None:
        if self.is_pressed:
            self._release(0, notify)

    # --- внутреннее ---
    def _release(self, release_velocity: int, notify: bool = True) -> None:
        self.is_pressed = False
        self.release_velocity = release_velocity
        try:
            if notify and self.on_release:
                self.on_release(self)  # held_time, velocity, release_velocity доступны
        finally:
            self.velocity = 0
            self.pressed_at = None

class ChordBinding:
    def __init__(self, notes, on_press=None, on_release=None, channel=None):
        self.notes = frozenset(notes)
        self.on_press = on_press
        self.on_release = on_release
        self.channel = channel

        self.held = set()
        self.is_pressed = False
        self.pressed_at = None

    @property
    def held_time(self) -> float:
        return 0.0 if self.pressed_at is None else time.monotonic() - self.pressed_at

    def handle(self, msg: md.Message) -> bool:
        if msg.type == "control_change" and msg.control in _PANIC_CONTROLS:
            if self.channel is None or msg.channel == self.channel:
                self.reset()
            return False

        if msg.type not in ("note_on", "note_off") or msg.note not in self.notes:
            return False
        if self.channel is not None and msg.channel != self.channel:
            return False

        if msg.type == "note_on" and msg.velocity > 0:
            self.held.add(msg.note)
            if not self.is_pressed and self.held == self.notes:
                self.is_pressed = True
                self.pressed_at = time.monotonic()
                if self.on_press:
                    self.on_press(self)
        else:
            self.held.discard(msg.note)
            if self.is_pressed:
                self._release()
        return True

    def reset(self, notify: bool = True) -> None:
        self.held.clear()
        if self.is_pressed:
            self._release(notify)

    def _release(self, notify: bool = True) -> None:
        self.is_pressed = False
        try:
            if notify and self.on_release:
                self.on_release(self)
        finally:
            self.pressed_at = None
