"""
Guides the user through first-time pairing with the Hue bridge.

The Hue bridge uses a "link button" flow:
  1. Physically press the button on top of the bridge.
  2. Within 30 seconds, POST to /api to create a new API user.
  3. Store the returned username for future requests.
"""

import json
import time
from pathlib import Path

import requests

# Default file to persist the username so pairing is only done once
DEFAULT_CONFIG_FILE = Path.home() / ".hue_controller.json"

# App name sent to the bridge during pairing
APP_NAME = "hue_controller#python"


def load_api_key(ip: str, config_file: Path = DEFAULT_CONFIG_FILE) -> str | None:
    """Return the stored API key for the given bridge IP, or None if not found."""
    if not config_file.exists():
        return None
    try:
        config = json.loads(config_file.read_text())
        return config.get(ip)
    except (json.JSONDecodeError, OSError):
        return None


def save_api_key(ip: str, api_key: str, config_file: Path = DEFAULT_CONFIG_FILE) -> None:
    """Persist the bridge API key to a JSON config file."""
    config: dict = {}
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    config[ip] = api_key
    config_file.write_text(json.dumps(config, indent=2))


def pair_bridge(ip: str, config_file: Path = DEFAULT_CONFIG_FILE, timeout: int = 30) -> str:
    """
    Interactively pair with the Hue bridge and return the API key.

    Instructs the user to press the physical link button on the bridge,
    then polls until the API key is granted or the timeout is reached.

    Args:
        ip:          IP address of the Hue bridge.
        config_file: Path to the JSON file where the API key is stored.
        timeout:     Seconds to wait for the button press (default 30).

    Returns:
        The API key granted by the bridge.

    Raises:
        TimeoutError: If the button is not pressed within `timeout` seconds.
        RuntimeError: If the bridge returns an unexpected error.
    """
    print(
        "\n[Hue Setup] Press the link button on top of your Hue bridge now.\n"
        f"            Waiting up to {timeout} seconds…"
    )

    url = f"http://{ip}/api"
    payload = {"devicetype": APP_NAME}
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Could not reach the bridge at {ip}: {exc}") from exc

        results = response.json()
        if isinstance(results, list) and results:
            result = results[0]
            if "success" in result:
                api_key = result["success"]["username"]
                save_api_key(ip, api_key, config_file)
                print(f"[Hue Setup] Paired successfully! API key saved to {config_file}")
                return api_key
            error = result.get("error", {})
            # Error type 101 = link button not pressed yet — keep polling
            if error.get("type") != 101:
                raise RuntimeError(f"Bridge error: {error.get('description', result)}")

        time.sleep(2)

    raise TimeoutError(
        "Link button was not pressed in time. Please try again."
    )
