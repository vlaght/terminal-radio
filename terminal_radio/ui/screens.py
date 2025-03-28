from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, ProgressBar, ListView, Footer
from textual.containers import Container, Horizontal, Vertical


class MainScreen(Screen):
    """Main application screen."""

    def __init__(self, player_controller, station_controller):
        super().__init__()
        self.player_controller = player_controller
        self.station_controller = station_controller
        self.selected_station = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Container(
            Horizontal(
                Button("Play", id="play", variant="success"),
                Button("Stop", id="stop", variant="error"),
                classes="controls",
            ),
            Horizontal(
                Button("-", id="volume_down"),
                Button("🔇", id="mute", variant="default"),
                ProgressBar(total=100, id="volume", show_eta=False),
                Button("+", id="volume_up"),
                classes="volume",
            ),
            ListView(id="stations"),
            classes="main",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load stations when screen is mounted."""
        stations = self.station_controller.get_stations()
        self.query_one("#volume", ProgressBar).progress = self.player_controller.volume
        stations_list = self.query_one("#stations", ListView)
        for station in stations:
            stations_list.append(station["name"])

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
            button = self.query_one("#mute", Button)
            button.label = "🔊" if not self.player_controller.is_muted else "🔇"

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle station selection."""
        self.selected_station = self.station_controller.get_stations()[event.index]

    def update_volume(self, volume: int) -> None:
        """Update the volume progress bar."""
        self.query_one("#volume", ProgressBar).progress = volume

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

    #mute {
        width: 4;
    }

    Button {
        margin: 1;
    }

    #stations {
        height: 100%;
        border: solid $primary;
    }
    """
