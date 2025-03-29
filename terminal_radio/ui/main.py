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
from terminal_radio.controllers.stations import station_to_dom_node


class MainScreen(Screen):
    """Main application screen."""

    BINDINGS = [
        ("enter", "select_station", "Select"),
        ("f", "search", "Search"),  # Add new binding
    ]

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
                Label("Volume level", id="volume_label"),
                ProgressBar(total=100, id="volume", show_eta=False),
                classes="volume",
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
        stations_list.children[0].add_class("-selected")

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
        await self.player_controller.start_playback(self.selected_station.url)
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

    .volume {
        height: 3;
        align: center middle;
        width: 100%;
    }

    #volume {
        width: 100%;
    }
    #volume_label {
        padding: 0 1;
    }
    #status_bar {
        padding: 0 1;
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
