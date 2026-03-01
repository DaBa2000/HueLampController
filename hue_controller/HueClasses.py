"""
Data models for Philips Hue entities (Light, Room, Scene).
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LightState:
    """Represents the current state of a light."""
    on: bool
    brightness: Optional[int] = None       # 1–254
    hue: Optional[int] = None             # 0–65535
    saturation: Optional[int] = None      # 0–254
    color_temp: Optional[int] = None      # 153–500 mired
    xy: Optional[list[float]] = None      # CIE XY color point
    reachable: bool = True

    @staticmethod
    def from_api(data: dict) -> "LightState":
        return LightState(
            on=data.get("on", False),
            brightness=data.get("bri"),
            hue=data.get("hue"),
            saturation=data.get("sat"),
            color_temp=data.get("ct"),
            xy=data.get("xy"),
            reachable=data.get("reachable", True),
        )


@dataclass
class Light:
    """Represents a single Hue light."""
    id: str
    name: str
    model: str
    state: LightState

    @staticmethod
    def from_api(light_id: str, data: dict) -> "Light":
        return Light(
            id=light_id,
            name=data.get("name", "Unknown"),
            model=data.get("modelid", ""),
            state=LightState.from_api(data.get("state", {})),
        )

    def __repr__(self):
        status = "on" if self.state.on else "off"
        return f"Light(id={self.id!r}, name={self.name!r}, status={status})"


@dataclass
class Room:
    """Represents a Hue room (group of lights)."""
    id: str
    name: str
    light_ids: list[str]
    room_type: str        # e.g. 'Bedroom', 'LivingRoom'
    scene_id: Optional[str] = None   # currently active scene

    @staticmethod
    def from_api(group_id: str, data: dict) -> "Room":
        return Room(
            id=group_id,
            name=data.get("name", "Unknown"),
            light_ids=data.get("lights", []),
            room_type=data.get("class", "Other"),
            scene_id=data.get("state", {}).get("scene"),
        )

    def __repr__(self):
        return f"Room(id={self.id!r}, name={self.name!r}, lights={self.light_ids})"


@dataclass
class Scene:
    """Represents a Hue scene (stored light configurations for a room)."""
    id: str
    name: str
    group_id: str       # the room this scene belongs to
    light_ids: list[str] = field(default_factory=list)

    @staticmethod
    def from_api(scene_id: str, data: dict) -> "Scene":
        return Scene(
            id=scene_id,
            name=data.get("name", "Unknown"),
            group_id=data.get("group", ""),
            light_ids=data.get("lights", []),
        )

    def __repr__(self):
        return f"Scene(id={self.id!r}, name={self.name!r}, group={self.group_id!r})"
