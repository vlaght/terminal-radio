import json
from pathlib import Path
from typing import List, Dict


class StationController:
    """Manages radio station data."""

    def __init__(self):
        self.stations: List[Dict] = []
        self.config_path = Path.home() / ".config" / "terminal-radio" / "stations.json"
        self._load_stations()

    def _load_stations(self) -> None:
        """Load stations from config file."""
        if self.config_path.exists():
            self.stations = json.loads(self.config_path.read_text())
        else:
            self.stations = []
            self._save_stations()

    def _save_stations(self) -> None:
        """Save stations to config file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(self.stations, indent=2))

    def add_station(self, name: str, url: str) -> None:
        """Add a new station."""
        self.stations.append({"name": name, "url": url})
        self._save_stations()

    def remove_station(self, index: int) -> None:
        """Remove a station by index."""
        if 0 <= index < len(self.stations):
            self.stations.pop(index)
            self._save_stations()

    def get_stations(self) -> List[Dict]:
        """Get all stations."""
        return self.stations
