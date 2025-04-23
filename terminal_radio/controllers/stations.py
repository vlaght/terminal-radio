from dataclasses import dataclass, asdict
import json

from textual.widgets import ListItem, Label

from terminal_radio.controllers.options import OptionsController


@dataclass
class Station:
    name: str
    url: str
    id: int = 0


def station_to_dom_node(station: Station) -> ListItem:
    item = ListItem(
        Label(station.name),
        id=f"station-{station.id}",
        name=station.name,
    )
    item.station = station
    return item


class StationController:
    """Manages radio station data."""

    def __init__(self):
        self._stations: dict[int, Station] = {}
        self._next_id = 1
        self.config_path = OptionsController.DEFAULT_CONFIG_DIR / "stations.json"
        self._load_stations()

    def _load_stations(self) -> None:
        """Load stations from config file."""
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text())
            for station_data in data:
                station = Station(**station_data)
                self._stations[station.id] = station
            if self._stations:
                self._next_id = max(self._stations.keys()) + 1
        else:
            self._stations = {}
            self._save_stations()

    def _save_stations(self) -> None:
        """Save stations to config file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(station) for station in self._stations.values()]
        self.config_path.write_text(json.dumps(data, indent=2))

    def add_station(self, name: str, url: str) -> Station:
        """Add a new station."""
        station = Station(name=name, url=url, id=self._next_id)
        self._stations[self._next_id] = station
        self._next_id += 1
        self._save_stations()
        return station

    def get_stations(self) -> list[Station]:
        """Get all stations."""
        return list(self._stations.values())

    def get_station(self, station_id: int) -> Station | None:
        """Get station by ID."""
        return self._stations.get(station_id)

    def delete_station(self, station_id: int) -> None:
        """Delete a station by ID."""
        if station_id in self._stations:
            del self._stations[station_id]
            self._save_stations()

    def update_station(self, station_id: int, name: str, url: str) -> Station:
        """Update an existing station."""
        if station_id in self._stations:
            self._stations[station_id].name = name
            self._stations[station_id].url = url
            self._save_stations()
        return self._stations[station_id]
