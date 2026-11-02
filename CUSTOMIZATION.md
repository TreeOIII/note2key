
note2key by TreeOIII(or kebok), licensed under CC BY-NC 4.0,
link to github: (https://github.com/TreeOIII/note2key/tree/main)

### Basic Customization of Config

> **Note**: Because the config and the shell of mido are written in Python, you can have endless customization. Only the basic customization that I made for ease of use is described here.


To edit keybinds you need to edit the list `bindings: list[nb]` in the `piano_keybinds` file. There you can add two types of binds:
- Single note
- Group of notes

Groups of notes take priority when pressing keys, so if you have binds like these:
- C3 = JUMP
- B3 + C3 = ATTACK

the second bind (B3 + C3 = ATTACK) will take priority.


What does that mean?
When you are pressing B3 + C3, only the second bind (B3 + C3 = ATTACK) will be triggered.

> **Note**: if you press C3 first, and then press B3, both binds will be triggered. But if you press B3 first, and then C3, only the bind (B3 + C3 = ATTACK) will be triggered.

Let's talk about Single note binds first. To make a single note bind you need to add `nb()` to the list `bindings: list[nb]`. `nb()` has three options:
- **note=** `<int>`
- **on_press=** `<func>`
- **on_release=** `<func>`

**note=** is the note number. You can use the note C4 as a reference: it is number 60. After `=` you need to put the note number.

> **Note**: On some keyboards note 60 is C3.

**on_press=** Here you put the function that the note triggers on press.

**on_release=** Here you put the function that the note triggers on release.

For ease of writing the config, there is a `do()` function. You use it in the options **on_press=** and
**on_release=**. In the brackets you put the function that you want to call. It looks something like this:
```
on_press=do(<func>, <options>)
on_press=do(ms.player_press_forward, True)
```

If we didn't have that function, we would need to write `lambda b:` at the start of each function that we want to call.


> **Note**: the `do()` function does not pass the `b` object to your function. The `b` object stores most of the information about the note. More about it later.


So your bind will look something like this:
```
bindings: list[nb] = [
  ...
  nb(note=<note>, on_press=do(<func>, <options>), on_release=do(<func>, <options>)),
  ...
]
```
Analysis of the bind example:
```
nb(note=50, on_press=do(ms.player_press_forward, True), on_release=do(ms.player_press_forward, False))
```
This bind says that when we press note `50 (D3)`, we will trigger the function `ms.player_press_forward` (toggle forward movement) with the option `True` (toggle forward movement **on**), and on release we will trigger the function `ms.player_press_forward` (toggle forward movement) with the option `False` (toggle forward movement **off**). So when we press note D3 we will walk forward, and when we release note D3 we will stop moving.


Binds that use `Group of notes` are very similar to binds that use `Single note`.
The only differences between them are:
- To make a bind for a group of notes, we write `cb()` and not `nb()`
- Instead of the `note=<note>` option we have the `notes=(<note>, <note>, ...)` option.
 
So your bind with **Group of notes** will look something like this:
```
bindings: list[nb] = [
  ...
  cb(notes=(<note>, <note>, ...), on_press=do(<func>, <options>), on_release=do(<func>, <options>)),
  ...
]
```
Analysis of the bind example:
```
cb(notes=(71, 47), on_press=do(ms.player_inventory_select_slot, 0))
```
This bind says that when we press the notes `71 (B4), 47 (B2)`, we will trigger the function `ms.player_inventory_select_slot` (select slot `<slot_number>`) with the option `0` (select slot **0**).

> **Note**: In the bind you need to have `note=`/`notes=` and at least one of those options: `on_press=`, `on_release=`.

When making your own binds, you will sometimes need to call several functions from one bind, or even a bunch of code that you wrote yourself. To do that, simply make a function before the ``bindings: list[nb]`` list that will call the functions or code that you want.

So your bind with a custom function will look something like this:
```
def <your_function_name_1>():
  <code>

def <your_function_name_2>():
  <code>

bindings: list[nb] = [
  ...
  nb(note=<note>, on_press=do(<your_function_name_1>, <options>), on_release=do(<your_function_name_2>, <options>)),
  ...
]
```
Analysis of the bind example:
```
def sprint_start():
    ms.player_press_forward(True)
    ms.player_press_sprint(True)

def sprint_stop():
    ms.player_press_forward(False)
    ms.player_press_sprint(False)

bindings: list[nb] = [
    nb(note=55, on_press=do(sprint_start), on_release=do(sprint_stop)),
]
```
Pressing 55 (G3) starts sprinting forward, and releasing it stops.

### Information about notes that you can use (`b` object)
When a bind is triggered (on press or on release), `note_binding.py` passes the bind object `b`
to your function. You can read information about the note from it.

> **Note**: Each type of bind transfers different information.

**nb()**

| Information      | How to read it       | Notes                                        |
|------------------|----------------------| ---------------------------------------------|
| note             | `b.note`             | note number                                  |
| channel          | `b.channel`          | `None` if any channel                        |
| is_pressed       | `b.is_pressed`       | `True` on press, `False` on release          |
| velocity         | `b.velocity`         | how hard the note was pressed (1-127)        |
| release_velocity | `b.release_velocity` | always 0 on press                            |
| pressed_at       | `b.pressed_at`       | time of the press (`time.monotonic()`)       |
| held_time        | `b.held_time`        | seconds the note was held (about 0 on press) |

**cb()**

| Information      | How to read it     | Notes                                        |
|------------------|--------------------|----------------------------------------------|
| notes            | `sorted(b.notes)`  | all notes of the chord                       |
| held             | `sorted(b.held)`   | notes of the chord held right now            |
| channel          | `b.channel`        | `None` if any channel                        |
| is_pressed       | `b.is_pressed`     | `True` when the chord is complete            |
| pressed_at       | `b.pressed_at`     | time when the chord became complete          |
| held_time        | `b.held_time`      | seconds the chord was held                   |

To get this information, your function must have the parameter `b`:
```
def <your_function_name>(b):
  <code>
```
Analysis of the bind example:
```
def show_note(b):
    ms.echo(f"note={b.note} velocity={b.velocity} held={b.held_time:.2f}s")

bindings: list[nb] = [
    nb(note=50, on_press=show_note, on_release=show_note),
]
```
When you press and release note 50 (D3), a message with the note number, the velocity and
the time it was held appears in the chat. Here `:.2f` is an f-string option that rounds
the time to two decimal places.

> **Important**: pass such a function directly to `on_press=` / `on_release=`, **without** `do()`.
> `do()` doesn't pass `b` to the function.

### Little analysis of code in the piano_keybinds.py file

> **Note №1**: This section was made to help you quickly understand the code in the `piano_keybinds.py` file.
>
> **Note №2**: You don't have to follow all the sections, etc. They were made to make the code easier to understand. Once you understand the code, you can change the `piano_keybinds.py` file however you want.

Here we will briefly analyze the file `piano_keybinds.py`. You can analyze the file `note_binding.py` yourself. You will need to change the code in `note_binding.py` only when you want to heavily customize the script.
The file `piano_keybinds.py` is divided into 4 sections:
- libraries import
- custom functions
- list of binds
- main loop

- At the start of `custom functions` there is the `do()` function.

Then there is the function `pyj_camera_rotate` (we will talk about it later).

After that there are functions that are responsible for camera rotation.

The `bindings: list[nb]` list is divided into 3 sections:
- movement & actions the player can do
- camera rotation
- slot selection

The fourth section is responsible for the execution of the code, and for the operation of your binds. There is the `MIDI Message Router` (responsible for which messages from your MIDI keyboard reach the `note_binding.py` and in what order they reach it) and there is also a function called `md.open_input()`. It starts listening to the MIDI port that you use to transfer keystroke data from your MIDI keyboard to the `note_binding.py`.

### Pyjinn
In the `piano_keybinds.py` you may see this:
```
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

```
It is a function written in **Pyjinn**. It's a language that has Python syntax but integrates very deeply with Java programs. That function is responsible for rotating the camera.

You set the variables `yaw_speed` and `pitch_speed` with `pyj_camera_rotate.set("yaw_speed", <float>)` / `pyj_camera_rotate.set("pitch_speed", <float>)`. Then, if the speed isn't equal to 0, it rotates the player with these formulas: yaw: `yaw + yaw_speed * 4 * dt`, pitch: `pitch + pitch_speed * 4 * dt`. The formula for **yaw** is identical to the formula for **pitch**, so we will analyze only the formula for **yaw**.
```
yaw + yaw_speed * 4 * dt
```
First `yaw_speed` is multiplied by our sensitivity (currently 4), then by `dt` (Δtime), and the result is added to the current yaw, which becomes the new orientation.

We multiply `yaw_speed * 4` by `dt` (or Δtime, read as "delta time") to ensure that we have smooth motion and that the motion is not affected by the frame rate.

You can write your own functions with **Pyjinn** in the Python file, as we saw in the `piano_keybinds.py` file:
```
<your_function_name> = java.eval_pyjinn_script("""
...
...
""")
```
Or you can write an entire script using **Pyjinn** by making a file in the `minecraft/minescript/` folder with the `.pyj` extension. External Python libraries such as `mido` and `python-rtmidi` are not available in `.pyj` scripts, so `piano_keybinds.py` and `note_binding.py` are regular `.py` scripts with Pyjinn code embedded in them.
