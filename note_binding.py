import time
from dataclasses import dataclass, field
from typing import Callable, Optional

import mido as md

Callback = Callable[["NoteBinding"], None]

# Control Change, после которых все ноты считаются отпущенными
ALL_SOUND_OFF = 120
ALL_NOTES_OFF = 123
_PANIC_CONTROLS = (ALL_SOUND_OFF, ALL_NOTES_OFF)


@dataclass(eq=False)  # сравнение и хэш по идентичности объекта, а не по полям
class NoteBinding:
    note: int                                   # номер ноты MIDI (0-127)
    channel: Optional[int] = None               # None = любой канал
    on_press: Optional[Callback] = None         # один раз при нажатии
    on_release: Optional[Callback] = None       # один раз при отпускании

    # состояние (заполняется автоматически)
    is_pressed: bool = field(default=False, init=False)
    velocity: int = field(default=0, init=False)          # сила нажатия
    release_velocity: int = field(default=0, init=False)  # сила отпускания
    pressed_at: Optional[float] = field(default=None, init=False)

    @property
    def held_time(self) -> float:
        """Сколько секунд нота удерживается (0, если не нажата).

        Считается от pressed_at, поэтому корректно работает и внутри
        on_release: там is_pressed уже False, но pressed_at ещё не сброшен.
        """
        if self.pressed_at is None:
            return 0.0
        return time.monotonic() - self.pressed_at

    # --- декораторы для удобной привязки кода ---
    def press(self, fn: Callback) -> Callback:
        self.on_press = fn
        return fn

    def release(self, fn: Callback) -> Callback:
        self.on_release = fn
        return fn

    # --- работа с MIDI ---
    def matches(self, msg: md.Message) -> bool:
        return (
            msg.type in ("note_on", "note_off")
            and msg.note == self.note
            and (self.channel is None or msg.channel == self.channel)
        )

    def handle(self, msg: md.Message) -> bool:
        """Обновляет состояние по сообщению.
        Возвращает True, если оно относилось к этой ноте.

        All Sound Off / All Notes Off сбрасывают ноту, но возвращают False
        """
        if msg.type == "control_change" and msg.control in _PANIC_CONTROLS:
            if self.channel is None or msg.channel == self.channel:
                self.reset()
            return False

        if not self.matches(msg):
            return False

        if msg.type == "note_on" and not self.is_pressed:
            self.is_pressed = True
            self.velocity = msg.velocity
            self.release_velocity = 0
            self.pressed_at = time.monotonic()
            if self.on_press:
                self.on_press(self)

        elif msg.type == "note_off" and self.is_pressed:
            self._release(msg.velocity)

        return True

    def reset(self, notify: bool = True) -> None:
        """Принудительно отпускает ноту, если она зажата.

        Вызывать при отключении порта, выходе из программы и т.п.
        notify=True   on_release будет вызван (release_velocity = 0);
        notify=False  состояние сбрасывается молча.
        """
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
            # состояние сбрасывается, даже если колбэк бросил исключение;
            # release_velocity остаётся до следующего нажатия
            self.velocity = 0
            self.pressed_at = None

class ChordBinding:
    def __init__(self, notes, on_press=None, on_release=None, channel=None):
        self.notes = frozenset(notes)      # ноты (x, y, ...)
        self.on_press = on_press
        self.on_release = on_release
        self.channel = channel             # None = любой канал

        self.held = set()                  # какие ноты группы зажаты сейчас
        self.is_pressed = False            # зажат ли весь аккорд
        self.pressed_at = None

    @property
    def held_time(self) -> float:
        return 0.0 if self.pressed_at is None else time.monotonic() - self.pressed_at

    def handle(self, msg: md.Message) -> bool:
        # All Sound Off / All Notes Off
        if msg.type == "control_change" and msg.control in (120, 123):
            self.reset()
            return False

        if msg.type not in ("note_on", "note_off") or msg.note not in self.notes:
            return False
        if self.channel is not None and msg.channel != self.channel:
            return False

        # note_on с velocity 0 по стандарту MIDI означает отпускание
        if msg.type == "note_on" and msg.velocity > 0:
            self.held.add(msg.note)
            if not self.is_pressed and self.held == self.notes:
                self.is_pressed = True
                self.pressed_at = time.monotonic()
                if self.on_press:
                    self.on_press(self)
        else:
            self.held.discard(msg.note)
            if self.is_pressed:  # аккорд развалился
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