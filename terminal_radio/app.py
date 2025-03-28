# app.py

from textual.app import App, ComposeResult
from textual.widgets import Button
from textual.binding import Binding
from terminal_radio.controllers.player import PlayerController
from terminal_radio.controllers.stations import StationController
from terminal_radio.ui.screens import MainScreen
from pathlib import Path


class RadioPlayerApp(App):
    """A terminal-based internet radio player."""

    TITLE = "Terminal Radio Player"
    CSS_PATH = str(Path(__file__).parent / "assets" / "styles.css")
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("space", "toggle_playback", "Play/Pause", show=True),
        Binding("up", "volume_up", "Volume Up", show=True),
        Binding("down", "volume_down", "Volume Down", show=True),
        Binding("a", "add_station", "Add Station", show=True),
        Binding("e", "edit_station", "Edit Station", show=True),
        Binding("d", "delete_station", "Delete Station", show=True),
        Binding("f1", "toggle_help", "Help", show=True),
        Binding("m", "toggle_mute", "Mute/Unmute", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.player_controller = PlayerController()
        self.station_controller = StationController()

    async def on_mount(self) -> None:
        """Called when app is mounted."""
        self.main_screen = MainScreen(self.player_controller, self.station_controller)
        await self.push_screen(self.main_screen)

    async def action_toggle_playback(self) -> None:
        """Toggle playback state."""
        if self.player_controller.is_playing:
            await self.player_controller.stop_playback()
        else:
            await self.player_controller.start_playback()

    async def action_volume_up(self) -> None:
        """Increase volume."""
        await self.player_controller.change_volume(5)
        self.main_screen.update_volume(self.player_controller.volume)

    async def action_volume_down(self) -> None:
        """Decrease volume."""
        await self.player_controller.change_volume(-5)
        self.main_screen.update_volume(self.player_controller.volume)

    async def action_add_station(self) -> None:
        """Add a new station."""
        await self.push_screen("add_station")

    async def action_edit_station(self) -> None:
        """Edit selected station."""
        if self.main_screen.selected_station is not None:
            await self.push_screen("edit_station", self.main_screen.selected_station)

    async def action_delete_station(self) -> None:
        """Delete selected station."""
        if self.main_screen.selected_station is not None:
            await self.push_screen("confirm_delete", self.main_screen.selected_station)

    async def action_toggle_mute(self) -> None:
        """Toggle mute state."""
        await self.player_controller.toggle_mute()
        self.main_screen.update_volume(self.player_controller.volume)
        button = self.main_screen.query_one("#mute", Button)
        button.label = "🔊" if not self.player_controller.is_muted else "🔇"


if __name__ == "__main__":
    RadioPlayerApp.run()
