"""
HueController — the main entry point for controlling Philips Hue lights.

Usage:
    from hue_controller import HueController

    hue = HueController("192.168.1.10")       # pairs automatically if needed
    lights = hue.get_lights()
    hue.turn_on(lights[0])
    hue.set_brightness(lights[0], 128)
    hue.set_color_rgb(lights[0], 255, 100, 0)
"""

from pathlib import Path
from typing import Optional

from .HueAPI import HueAPI
from .ColorUtils import clamp, kelvin_to_mired, rgb_to_xy
from .HueClasses import Light, Room, Scene
from .HueBridgeSetup import DEFAULT_CONFIG_FILE, load_api_key, pair_bridge


class HueController:

    def __init__(
        self,
        ip: str,
        api_key: Optional[str] = None,
        config_file: Path = DEFAULT_CONFIG_FILE,
    ):
        self.ip = ip
        self._config_file = config_file

        # Resolve API key: argument → config file → interactive pairing
        if api_key is None:
            api_key = load_api_key(ip, config_file)
        if api_key is None:
            api_key = pair_bridge(ip, config_file)

        self._api = HueAPI(ip, api_key)
        self.api_key = api_key

        print(f"Connected to Hue bridge at {ip} with API key: {api_key}")

    # ------------------------------------------------------------------
    # Lights
    # ------------------------------------------------------------------

    def get_lights(self) -> list[Light]:
        raw = self._api.get_lights()
        return [Light.from_api(lid, data) for lid, data in raw.items()]

    def get_light(self, light_id: str) -> Light:
        data = self._api.get_light(light_id)
        return Light.from_api(light_id, data)

    def turn_on(self, light: Light | str) -> None:
        self._api.set_light_state(self._id(light), {"on": True})

    def turn_off(self, light: Light | str) -> None:
        self._api.set_light_state(self._id(light), {"on": False})

    def set_brightness(self, light: Light | str, brightness: int) -> None:
        bri = clamp(brightness, 1, 254)
        self._api.set_light_state(self._id(light), {"on": True, "bri": bri})

    def set_color_rgb(self, light: Light | str, red: int, green: int, blue: int) -> None:
        x, y = rgb_to_xy(red, green, blue)
        self._api.set_light_state(self._id(light), {"on": True, "xy": [x, y]})

    def set_color_hue_sat(self, light: Light | str, hue: int, saturation: int) -> None:
        state = {
            "on": True,
            "hue": clamp(hue, 0, 65535),
            "sat": clamp(saturation, 0, 254),
        }
        self._api.set_light_state(self._id(light), state)

    def set_color_temp(self, light: Light | str, kelvin: int) -> None:
        ct = clamp(kelvin_to_mired(kelvin), 153, 500)
        self._api.set_light_state(self._id(light), {"on": True, "ct": ct})

    # ------------------------------------------------------------------
    # Rooms (Groups)
    # ------------------------------------------------------------------

    def get_rooms(self) -> list[Room]:
        raw = self._api.get_groups()
        # Only return group type "Room" (not zones or entertainment areas)
        return [
            Room.from_api(gid, data)
            for gid, data in raw.items()
            if data.get("type") == "Room"
        ]

    def get_room(self, room_id: str) -> Room:
        data = self._api.get_group(room_id)
        return Room.from_api(room_id, data)

    def turn_on_room(self, room: Room | str) -> None:
        self._api.set_group_action(self._id(room), {"on": True})

    def turn_off_room(self, room: Room | str) -> None:
        self._api.set_group_action(self._id(room), {"on": False})

    def set_room_brightness(self, room: Room | str, brightness: int) -> None:
        bri = clamp(brightness, 1, 254)
        self._api.set_group_action(self._id(room), {"on": True, "bri": bri})

    # ------------------------------------------------------------------
    # Scenes
    # ------------------------------------------------------------------

    def get_scenes(self) -> list[Scene]:
        raw = self._api.get_scenes()
        return [Scene.from_api(sid, data) for sid, data in raw.items()]

    def get_scenes_for_room(self, room: Room | str) -> list[Scene]:
        room_id = self._id(room)
        return [s for s in self.get_scenes() if s.group_id == room_id]

    def activate_scene(self, scene: Scene | str, room: Room | str) -> None:
        self._api.activate_scene(self._id(room), self._id(scene))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _id(obj: object) -> str:
        if isinstance(obj, str):
            return obj
        if hasattr(obj, "id"):
            return obj.id
        raise TypeError(f"Expected a model object or string ID, got {type(obj)}")
