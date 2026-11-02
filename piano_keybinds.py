# piano_keybinds.py

import mido as md
import minescript as ms
from note_binding import NoteBinding as nb
from note_binding import ChordBinding as cb

import java

# --- custom functions ---

def do(fn, *args):
    return lambda b: fn(*args)

pyj_camera_rotate = java.eval_pyjinn_script("""
yaw_speed = 0.0
pitch_speed = 0.0
System = JavaClass("java.lang.System")
last = System.nanoTime()

def on_render(event):
  global last
  now = System.nanoTime()
  dt = (now - last) / 1e9
  last = now
  if yaw_speed != 0.0:
    yaw, pitch = player_orientation()
    player_set_orientation(yaw + yaw_speed * 4 * dt, pitch)
  if pitch_speed != 0.0:
    yaw, pitch = player_orientation()
    player_set_orientation(yaw, pitch + pitch_speed * 4 * dt)

add_event_listener("render", on_render)
""")

def rotate_right(b: nb):
    pyj_camera_rotate.set("yaw_speed", float(b.velocity))
def rotate_left(b: nb):
    pyj_camera_rotate.set("yaw_speed", -float(b.velocity))

def rotate_up(b: nb):
    pyj_camera_rotate.set("pitch_speed", -float(b.velocity))
def rotate_down(b: nb):
    pyj_camera_rotate.set("pitch_speed", float(b.velocity))

def rotate_stop(b: nb):
    pyj_camera_rotate.set("yaw_speed", 0.0)
    pyj_camera_rotate.set("pitch_speed", 0.0)

# --- list of binds ---
bindings: list[nb] = [
    nb(note=50, on_press=do(ms.player_press_forward, True), on_release=do(ms.player_press_forward, False)), #ms.player_press_forward
    nb(note=49, on_press=do(ms.player_press_left, True), on_release=do(ms.player_press_left, False)), #ms.player_press_left
    nb(note=51, on_press=do(ms.player_press_right, True), on_release=do(ms.player_press_right, False)), #ms.player_press_right
    nb(note=53, on_press=do(ms.player_press_jump, True), on_release=do(ms.player_press_jump, False)), #ms.player_press_jump
    nb(note=52, on_press=do(ms.player_press_attack, True), on_release=do(ms.player_press_attack, False)), #ms.player_press_attack
    nb(note=48, on_press=do(ms.player_press_use, True), on_release=do(ms.player_press_use, False)), #ms.player_press_use
    nb(note=47, on_press=do(ms.player_press_sneak, True), on_release=do(ms.player_press_sneak, False)), #ms.player_press_sneak

    nb(note=69, on_press=rotate_right, on_release=rotate_stop),
    nb(note=67, on_press=rotate_left, on_release=rotate_stop),
    nb(note=65, on_press=rotate_up, on_release=rotate_stop),
    nb(note=64, on_press=rotate_down, on_release=rotate_stop),

    cb(notes=(71, 47), on_press=do(ms.player_inventory_select_slot, 0)),
    cb(notes=(71, 48), on_press=do(ms.player_inventory_select_slot, 1)),
    cb(notes=(71, 50), on_press=do(ms.player_inventory_select_slot, 2)),
    cb(notes=(71, 52), on_press=do(ms.player_inventory_select_slot, 3)),
    cb(notes=(71, 53), on_press=do(ms.player_inventory_select_slot, 4)),
    cb(notes=(71, 64), on_press=do(ms.player_inventory_select_slot, 5)),
    cb(notes=(71, 65), on_press=do(ms.player_inventory_select_slot, 6)),
    cb(notes=(71, 67), on_press=do(ms.player_inventory_select_slot, 7)),
    cb(notes=(71, 69), on_press=do(ms.player_inventory_select_slot, 8)),
]

# --- loop ---
chords = [b for b in bindings if isinstance(b, cb)]
singles = [b for b in bindings if not isinstance(b, cb)]


def dispatch(msg):
    for c in chords:
        c.handle(msg)

    if msg.type == "note_on" and msg.velocity > 0:
        if any(c.is_pressed and msg.note in c.notes for c in chords):
            return

    for s in singles:
        s.handle(msg)


def main():
    ms.echo("Ports:", md.get_input_names())

    with md.open_input() as port:
        ms.echo(f"Start listening to port: \"{port.name}\"")
        try:
            for msg in port:
                dispatch(msg)
        except KeyboardInterrupt:
            pass
        finally:
            for b in bindings:
                b.reset()


if __name__ == "__main__":
    main()
