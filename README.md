# note2key
Now you can play Minecraft with a MIDI keyboard!

## Requirements
- Minecraft 26.3 Fabric
- [Minescript 5.0+](https://modrinth.com/mod/minescript)
- [Python 3.11](https://www.python.org/downloads/)
- Library [mido](https://mido.readthedocs.io/en/latest/installing.html)
- Library python-rtmidi

## Installation
1. Install the [Minescript](https://modrinth.com/mod/minescript) mod from Modrinth
2. Open a terminal and type this command to install the mido library
```
<Insert full path to Python 3.11> -m pip install mido
```
3. Then type this command to install python-rtmidi
```
<Insert full path to Python 3.11> -m pip install python-rtmidi
```
4. Download the files note_binding.py and piano_keybinds.py from [Releases](https://github.com/TreeOIII/note2key/releases)
5. After the first game launch, put the file piano_keybinds.py into `minecraft/minescript`, and the file note_binding.py into `minecraft/minescript/system/lib`
6. Put the full path to Python 3.11 into `minecraft/minescript/config.txt`. The file will look something like this:
```
# Lines starting with "#" are ignored.

python="C:\Users\NAME\AppData\Local\Programs\Python\Python311\python.exe"
```

## Usage
1. Connect your MIDI keyboard.
2. In the game chat, type:
   ```
   \piano_keybinds
   ```


## Default keybinds
    Note numbering: middle C = C4 (MIDI 60). If your keyboard labels it C3, shift everything by one octave.

Movement and actions:
- D3: forward
- C#3: left
- D#3: right
- F3: jump
- E3: attack (left click)
- C3: use (right click)
- B2: sneak

Camera rotation:
- A4: right
- G4: left
- F4: up
- E4: down

Hotbar slot selection (hold B4 first):
- B4 + B2: slot 1
- B4 + C3: slot 2
- B4 + D3: slot 3
- B4 + E3: slot 4
- B4 + F3: slot 5
- B4 + E4: slot 6
- B4 + F4: slot 7
- B4 + G4: slot 8
- B4 + A4: slot 9


## Troubleshooting
- **ModuleNotFoundError: No module named 'mido'**: the libraries were installed for a different Python than the one Minescript uses.
- No errors, but the script doesn't work: when you run the script, it starts listening to the first MIDI port. It may not be the correct one. When you run the script, you'll get a message like this:
```
Ports:['CASIO USB-MIDI 0', 'Arturia KeyStep 32 0', etc]
Start listening to port: CASIO USB-MIDI 0
```
  On line 97 of the `piano_keybinds.py` script there is a function `md.open_input()`. Try inserting different ports from the list in the brackets of the function. Most likely the script is just listening to the wrong port.
