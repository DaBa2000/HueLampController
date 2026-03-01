import requests
from typing import Any


class HueAPIError(Exception):
    pass


class HueAPI:

    def __init__(self, ip: str, username: str):
        self.base_url = f"http://{ip}/api/{username}"
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    # ------------------------------------------------------------------
    # Core HTTP helpers
    # ------------------------------------------------------------------

    def get(self, endpoint: str) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self._session.get(url, timeout=5)
        response.raise_for_status()
        return self._parse(response.json())

    def put(self, endpoint: str, data: dict) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self._session.put(url, json=data, timeout=5)
        response.raise_for_status()
        return self._parse(response.json())

    def post(self, endpoint: str, data: dict) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self._session.post(url, json=data, timeout=5)
        response.raise_for_status()
        return self._parse(response.json())

    # ------------------------------------------------------------------
    # Endpoint methods
    # ------------------------------------------------------------------

    def get_lights(self) -> dict:
        return self.get("lights")

    def get_light(self, light_id: str) -> dict:
        return self.get(f"lights/{light_id}")

    def set_light_state(self, light_id: str, state: dict) -> Any:
        return self.put(f"lights/{light_id}/state", state)

    def get_groups(self) -> dict:
        return self.get("groups")

    def get_group(self, group_id: str) -> dict:
        return self.get(f"groups/{group_id}")

    def set_group_action(self, group_id: str, action: dict) -> Any:
        return self.put(f"groups/{group_id}/action", action)

    def get_scenes(self) -> dict:
        return self.get("scenes")

    def activate_scene(self, group_id: str, scene_id: str) -> Any:
        return self.put(f"groups/{group_id}/action", {"scene": scene_id})

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _parse(self, response: Any) -> Any:
        """Detect API-level errors in successful HTTP responses."""
        if isinstance(response, list):
            for item in response:
                if "error" in item:
                    desc = item["error"].get("description", "Unknown API error")
                    raise HueAPIError(desc)
        return response
