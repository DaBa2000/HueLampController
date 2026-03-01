# HueLampController

Python module for controlling Philips Hue lights via the local bridge API.

## Setup

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from hue_controller import HueController

hue = HueController("192.168.1.10")   # pairing wizard runs on first use
```

On **first run** the controller will prompt you to press the physical link button
on top of your Hue bridge. After a successful pairing the API username is saved to
`~/.hue_controller.json` so subsequent runs connect immediately.

## Usage

### Lights

```python
lights = hue.get_lights()             # list[Light]
light  = hue.get_light("3")          # Light by ID

hue.turn_on(light)
hue.turn_off(light)
hue.set_brightness(light, 200)             # 1–254
hue.set_color_rgb(light, 255, 80, 0)      # RGB 0–255
hue.set_color_hue_sat(light, 46920, 254)  # Hue 0–65535 / Sat 0–254
hue.set_color_temp(light, 3000)           # Kelvin (≈ 2000–6500)
```

### Rooms

```python
rooms = hue.get_rooms()            # list[Room]
room  = hue.get_room("1")         # Room by ID

hue.turn_on_room(room)
hue.turn_off_room(room)
hue.set_room_brightness(room, 150)
```

### Scenes

```python
scenes      = hue.get_scenes()               # all scenes
room_scenes = hue.get_scenes_for_room(room)  # scenes for a room
hue.activate_scene(scene, room)              # activate
```

## Project Structure

```
hue_controller/
├── __init__.py      # public exports
├── controller.py    # HueController — main entry point
├── api.py           # low-level HTTP wrapper for the bridge
├── models.py        # Light, Room, Scene dataclasses
├── setup.py         # first-time pairing / username persistence
└── color.py         # RGB→XY and Kelvin→Mired conversions
example.py           # runnable quick-start demo
requirements.txt
```

## Finding Your Bridge IP

Open the Hue app → **Settings → My Hue System → Bridge** or visit
[discovery.meethue.com](https://discovery.meethue.com) on your local network.