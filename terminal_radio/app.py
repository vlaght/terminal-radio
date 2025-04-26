# app.py

import logging
from textual.app import App
from textual.widgets import ListView
from textual.binding import Binding
from textual import on

from terminal_radio.controllers.log import LogController
from terminal_radio.controllers.options import OptionsController
from terminal_radio.controllers.player import PlayerController
from terminal_radio.controllers.stations import StationController
from terminal_radio.ui.add_station import AddStationScreen
from terminal_radio.ui.edit_station import EditStationScreen
from terminal_radio.ui.log import LogScreen
from terminal_radio.ui.options import OptionsScreen
from terminal_radio.ui.quit import QuitScreen
from terminal_radio.ui.delete_station import ConfirmDeleteScreen
from terminal_radio.ui.main import MainScreen
from terminal_radio.ui.search import SearchScreen


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
        Binding("f", "search", "Search Stations", show=True),
        Binding("l", "log", "Log", show=True),
        Binding("o", "options_screen", "Options", show=True),
    ]

    SCREENS = {
        "add_station": AddStationScreen,
        "quit_screen": QuitScreen,
        "search_screen": SearchScreen,
        "options_screen": OptionsScreen,
    }

    def __init__(self):
        super().__init__()
        self.player_controller = PlayerController()
        self.station_controller = StationController()
        self.log_controller = LogController()
        self.options_controller = OptionsController()

    async def on_mount(self) -> None:
        """Called when app is mounted."""
        self.main_screen = MainScreen(
            player_controller=self.player_controller,
            station_controller=self.station_controller,
            options_controller=self.options_controller,
        )
        await self.push_screen(self.main_screen)
        self.log_controller.log(logging.DEBUG, "App mounted")
        self.theme = self.options_controller.options.theme

    async def action_toggle_playback(self) -> None:
        """Toggle playback state."""
        try:
            if self.player_controller.is_playing:
                await self.player_controller.stop_playback()
                self.main_screen.update_status("Pause")
            else:
                if not self.main_screen.selected_station:
                    self.notify(
                        "select station at first",
                        title="Not so fast",
                        severity="warning",
                    )
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
                        msg = "Failed to start playback"
                        self.notify(
                            msg,
                            title="Woopsie",
                            severity="error",
                        )
                        self.app.log_controller.log(logging.ERROR, msg)
        except Exception as e:
            error_msg = str(e).split("\n")[0]
            self.app.notify(
                message=error_msg[:50],
                title="error",
                severity="error",
                timeout=3,
            )
            self.app.log_controller.log(logging.ERROR, error_msg)

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
        stations = self.main_screen.query_one("#stations", ListView)
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
        selected_station = self.main_screen.selected_station
        # raise NotImplementedError(self.player_controller.is_muted, self.player_controller.volume)
        if muted_now:
            self.main_screen.update_status("Muted")
        elif not muted_now and self.player_controller.is_playing and selected_station:
            self.main_screen.update_status(f"Now playing: {selected_station.name}")
        else:
            self.main_screen.update_status(
                "Scroll stations with arrows, enter to select"
            )

    async def action_search(self) -> None:
        """Handle search action."""
        stations = self.station_controller.get_stations()
        await self.push_screen(SearchScreen(stations))

    async def action_log(self) -> None:
        """Handle log action."""
        log = self.app.log_controller.get_log()
        await self.push_screen(LogScreen(log))

    def on_search_screen_selected(self, message: SearchScreen.Selected) -> None:
        """Handle station selection from search screen."""
        self.main_screen.selected_station_by_id(message.station_id)

    async def action_request_quit(self) -> None:
        """Handle quit request."""
        await self.push_screen("quit_screen")

    async def action_options_screen(self) -> None:
        """Handle options screen action."""
        await self.push_screen(
            OptionsScreen(options_controller=self.options_controller),
        )

    @on(OptionsScreen.CONFIG_UPDATED_EVENT)
    async def handle_options_update(
        self, event: OptionsScreen.CONFIG_UPDATED_EVENT
    ) -> None:
        self.app.log_controller.log(
            logging.DEBUG,
            "Options updated",
        )
        if (
            self.options_controller.options.output_device is not None
            and self.options_controller.options.output_device
            != self.player_controller.get_output_device()
        ):
            was_playing = False
            if self.player_controller.is_playing:
                await self.player_controller.stop_playback()
                was_playing = True

            self.player_controller.set_output_device(
                self.options_controller.options.output_device,
            )
            if was_playing and self.main_screen.selected_station:
                await self.player_controller.start_playback(
                    self.main_screen.selected_station.url
                )
        if self.options_controller.options.theme != self.app.theme:
            self.app.theme = self.options_controller.options.theme


def main() -> None:
    """Run the application."""

    app = RadioPlayerApp()
    app.run()


if __name__ == "__main__":
    main()
