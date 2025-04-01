from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Button,
    Label,
    ProgressBar,
    ListView,
    Footer,
    Static,
    Header,
    ListItem,
)
from textual.containers import Container, Horizontal
from textual.timer import Timer
from terminal_radio.controllers.stations import station_to_dom_node
import requests
from urllib.parse import urlparse
import socket
from concurrent.futures import ThreadPoolExecutor
import asyncio
import time


class MainScreen(Screen):
    """Main application screen."""

    BINDINGS = [
        ("enter", "select_station", "Select"),
        ("f", "search", "Search"),  # Add new binding
    ]
    latency_update_timer: Timer

    def __init__(self, player_controller, station_controller):
        super().__init__()
        self.player_controller = player_controller
        self.station_controller = station_controller
        self.selected_station = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Container(
            Header(),
            Horizontal(
                Horizontal(
                    Label("Volume level", id="volume_label"),
                    ProgressBar(total=100, id="volume", show_eta=False),
                    id="volume_panel",
                ),
                Horizontal(
                    Label("Station Latency", id="latency_label"),
                    Label(
                        "0000",
                        id="latency_digits",
                    ),
                    id="latency_panel",
                ),
                classes="top_panel",
            ),
            Static("No station playing", id="status_bar", classes="status"),
            ListView(id="stations"),
            classes="main",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load stations when screen is mounted."""
        # Set initial volume
        initial_volume = self.player_controller.volume
        self.query_one("#volume", ProgressBar).progress = initial_volume
        self.update_status("arrows to scroll stations, enter to select")
        # Load stations
        stations = self.station_controller.get_stations()
        stations_list = self.query_one("#stations", ListView)
        for station in stations:
            item = station_to_dom_node(station)
            stations_list.append(item)
        self.selected_station = stations[0] if stations else None
        if stations_list.children:
            stations_list.children[0].add_class("-selected")
        self.latency_update_timer = self.set_interval(3, self.update_latency)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if button_id == "play":
            self.app.action_toggle_playback()
        elif button_id == "stop":
            self.app.action_toggle_playback()
        elif button_id == "volume_up":
            self.app.action_volume_up()
        elif button_id == "volume_down":
            self.app.action_volume_down()
        elif button_id == "mute":
            self.app.action_toggle_mute()

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle station selection."""
        self.selected_station = event.item.station
        self.query("#stations > ListItem").remove_class("-selected")
        event.item.add_class("-selected")
        if self.player_controller.is_playing:
            await self.player_controller.stop_playback()
        try:
            await self.player_controller.start_playback(self.selected_station.url)
        except Exception as e:
            self.notify(str(e), title="Error", severity="error")
        else:
            self.update_status(f"Now playing: {self.selected_station.name}")

    def update_volume(self, volume: int) -> None:
        """Update the volume progress bar."""
        self.query_one("#volume", ProgressBar).progress = volume

    def update_status(self, status: str | None) -> None:
        """Update the status bar with current station."""
        status_bar = self.query_one("#status_bar", Static)
        if status:
            status_bar.update(status)
        else:
            status_bar.update("No station playing")

    def selected_station_by_id(self, station_id: str) -> None:
        """Set the selected station by ID."""
        station_list = self.query_one("#stations", ListView).remove_class("-selected")
        target_station = self.query_one(f"#station-{station_id}", ListItem).add_class(
            "-selected"
        )
        station_list.index = station_list.children.index(target_station)
        station_list.action_select_cursor()

    def measure_latency(self, url: str) -> float:
        """Measure network latency to the station server."""
        try:
            parsed = urlparse(url)
            host = parsed.netloc
            if not host:
                return 0.0

            start_time = time.time()
            response = requests.head(url, timeout=2)
            latency = (time.time() - start_time) * 1000
            return latency
        except Exception:
            return 999.0

    async def update_latency(self) -> None:
        """Update latency display with actual network measurement."""
        if not self.selected_station or not self.player_controller.is_playing:
            self.query_one("#latency_digits", Label).update("0000")
            return

        # Run the network request in a thread pool to avoid blocking
        with ThreadPoolExecutor() as executor:
            latency = await asyncio.get_event_loop().run_in_executor(
                executor,
                self.measure_latency,
                self.selected_station.url
            )

        value = str(int(latency)).zfill(4) if latency < 1000 else ">999"
        label = self.query_one("#latency_digits", Label)
        label.update(value)

    CSS = """
    .main {
        layout: vertical;
        background: $surface;
        padding: 1;
        height: 100%;
    }

    .controls {
        height: 3;
        align: center middle;
    }

    .top_panel {
        height: auto;
        align: left middle;
        width: 100%;
        margin: 1 1;
    }


    #volume_label {
        padding: 0 1;
    }
    #volume {
        padding: 0 1;
        color: $accent;
    }
    #volume_panel {
        border: solid $primary;
        height: auto;
        width: auto;
    }

    #latency_digits {
        color: $accent;
        align: right middle;
        margin: 0 2;
        padding: 0 2;
    }
    #latency_label {
        padding: 0 1;
    }
    #latency_panel {
        border: solid $primary;
        height: auto;
        width: auto;
    }

    #status_bar {
        padding: 0 1;
        margin: 1 1;
    }

    Button {
    }

    #stations {
        height: 1fr;  # Changed from 100% to 1fr
        border: solid $primary;
        overflow-y: scroll;
        width: 100%;
        padding: 0 1;
    }

    ListView > ListItem {
        padding: 0 2;
    }

    ListView > ListItem:hover {
        background: $accent;
    }

    ListView > ListItem.-selected {
        background: $primary;
        color: $text;
    }

    .status {
        height: 1;
        align: center middle;
        background: $secondary;
        color: $text;
    }
    """
