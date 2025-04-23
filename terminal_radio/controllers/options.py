from dataclasses import dataclass
import json
from pathlib import Path
import sounddevice as sd


@dataclass
class Options:
    output_device: int | None = None
    theme: str = "textual-dark"


class OptionsController:
    DEFAULT_CONFIG_DIR = Path.home() / ".config" / "terminal-radio"
    DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "options.json"

    def __init__(self) -> None:
        self.config_path = self.DEFAULT_CONFIG_PATH
        if self.config_path.exists():
            with self.config_path.open("r") as f:
                try:
                    options = Options(**json.load(f))
                except json.JSONDecodeError as exc:
                    raise ValueError("Invalid JSON format in options file.") from exc
                self.options = options
        else:
            self.DEFAULT_CONFIG_DIR.parent.mkdir(parents=True, exist_ok=True)
            self.options = Options()
            if devices := self.get_available_devices():
                self.update_options(output_device=devices[0][1])

    def persist_options(self) -> None:
        """Save options to the config file."""
        try:
            with self.config_path.open("w") as f:
                json.dump(self.options.__dict__, f, indent=4)
        except OSError as exc:
            raise RuntimeError(f"Failed to save options: {exc}") from exc
        except ValueError as exc:
            raise ValueError(f"Invalid data in options: {exc}") from exc

    def update_options(self, **kwargs) -> None:
        """Update options with new values."""
        for key, value in kwargs.items():
            if hasattr(self.options, key):
                setattr(self.options, key, value)
            else:
                raise ValueError(f"Unexpected config parameter: {key}")
        self.persist_options()

    @classmethod
    def get_available_devices(cls) -> list[tuple[str, int]]:
        """Get a list of available audio devices."""
        devices = sd.query_devices(kind="output")
        return (
            [(device["name"], device["index"]) for device in devices]
            if isinstance(devices, tuple)
            else [(devices["name"], devices["index"])]
        )
