# app.py

from textual.app import App
from textual.widgets import ListView
from textual.binding import Binding
from terminal_radio.controllers.player import PlayerController
from terminal_radio.controllers.stations import StationController
from terminal_radio.ui.add_station import AddStationScreen
from terminal_radio.ui.edit_station import EditStationScreen
from terminal_radio.ui.quit import QuitScreen
from terminal_radio.ui.delete_station import ConfirmDeleteScreen
from terminal_radio.ui.main import MainScreen


class RadioPlayerApp(App):
    """A terminal-based internet radio player."""

    TITLE = "Terminal Radio Player"
    BINDINGS = [
        Binding("q", "request_quit", "Quit", show=True),
        Binding("space", "toggle_playback", "Play/Pause", show=True),
        Binding("left", "volume_down", "Volume Down", show=True),
        Binding("right", "volume_up", "Volume Up", show=True),
        Binding("a", "add_station", "Add Station", show=True),
        Binding("e", "edit_station", "Edit Station", show=True),
        Binding("r", "remove_station", "Remove Station", show=True),
        Binding("m", "toggle_mute", "Mute/Unmute", show=True),
    ]

    SCREENS = {
        "add_station": AddStationScreen,
        "quit_screen": QuitScreen,
    }

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
        try:
            if self.player_controller.is_playing:
                await self.player_controller.stop_playback()
                self.main_screen.update_status("Pause")
            else:
                if not self.main_screen.selected_station:
                    self.main_screen.update_status("Error: No station selected")
                    return
                self.main_screen.update_status(
                    f"Loading: {self.main_screen.selected_station.name}"
                )
                if (
                    hasattr(self.main_screen, "selected_station")
                    and self.main_screen.selected_station
                ):
                    station = self.main_screen.selected_station
                    success = await self.player_controller.start_playback(station.url)
                    if success:
                        self.main_screen.update_status(f"Now playing: {station.name}")
                    else:
                        self.main_screen.update_status(
                            "Error: Failed to start playback"
                        )
        except Exception as e:
            error_msg = str(e).split("\n")[0]  # Get first line of error
            self.main_screen.update_status(f"Error: {error_msg}")

    async def action_volume_up(self) -> None:
        """Increase volume."""
        await self.player_controller.change_volume(5)
        volume = self.player_controller.volume
        self.main_screen.update_volume(volume)

    async def action_volume_down(self) -> None:
        """Decrease volume."""
        await self.player_controller.change_volume(-5)
        volume = self.player_controller.volume
        self.main_screen.update_volume(volume)

    async def action_add_station(self) -> None:
        """Add a new station."""
        await self.push_screen("add_station")

    async def action_edit_station(self) -> None:
        """Edit selected station."""
        stations = self.app.main_screen.query_one("#stations", ListView)
        if (
            stations
            and stations.highlighted_child
            and stations.highlighted_child.station
        ):
            await self.push_screen(
                EditStationScreen(stations.highlighted_child.station)
            )

    async def action_remove_station(self) -> None:
        """Delete selected station."""
        stations = self.children[0].query_one("#stations", ListView)
        if (
            stations
            and stations.highlighted_child
            and stations.highlighted_child.station
        ):
            await self.push_screen(
                ConfirmDeleteScreen(stations.highlighted_child.station)
            )

    async def action_toggle_mute(self) -> None:
        """Toggle mute state."""
        muted_now = await self.player_controller.toggle_mute()
        volume = self.player_controller.volume
        self.main_screen.update_volume(volume)
        # raise NotImplementedError(self.player_controller.is_muted, self.player_controller.volume)
        if muted_now:
            self.main_screen.update_status("Muted")
        elif not muted_now and self.player_controller.is_playing:
            self.main_screen.update_status(
                f"Now playing: {self.main_screen.selected_station.name}"
            )
        else:
            self.main_screen.update_status(
                "Scroll stations with arrows, enter to select"
            )

    async def action_request_quit(self) -> None:
        """Handle quit request."""
        await self.push_screen("quit_screen")


def main() -> None:
    """Run the application."""

    app = RadioPlayerApp()
    app.run()


if __name__ == "__main__":
    main()
