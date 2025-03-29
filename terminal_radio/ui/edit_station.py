from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input, ListView
from textual.containers import Horizontal, Vertical
from terminal_radio.controllers.stations import station_to_dom_node


class EditStationScreen(ModalScreen):
    """Screen for editing an existing station."""

    def __init__(self, station, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.station = station

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Edit Station", id="title"),
            Input(
                value=self.station.name,
                placeholder="Station Name",
                valid_empty=False,
                id="edit-name",
            ),
            Input(
                value=self.station.url,
                placeholder="Station URL",
                valid_empty=False,
                id="edit-url",
            ),
            Horizontal(
                Button("Save", variant="success", id="save"),
                Button("Cancel", variant="error", id="cancel"),
                id="buttons",
            ),
            id="edit-station-dialog",
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save":
            name = self.query_one("#edit-name", Input).value
            url = self.query_one("#edit-url", Input).value
            if name and url:
                station = self.app.station_controller.update_station(
                    self.station.id,
                    name,
                    url,
                )
                stations_list: ListView = self.app.main_screen.query_one(
                    "#stations", ListView
                )
                index_to_replace = stations_list.index
                await stations_list.pop(index_to_replace)
                await stations_list.insert(
                    index_to_replace, [station_to_dom_node(station)]
                )
                self.query_one("#edit-name", Input).focus()
                self.app.main_screen.update_status(f"Station '{name}' updated")

        self.app.pop_screen()

    def on_mount(self) -> None:
        """Set focus to the name input field."""
        self.query_one("#edit-name", Input).focus()

    def key_escape(self) -> None:
        """Handle escape key press."""
        self.app.pop_screen()

    CSS = """
    #edit-station-dialog {
        background: $surface;
        border: thick $accent;
        padding: 1;
        width: 60;
        height: auto;
        margin: 1 2;
    }

    #title {
        text-align: center;
        height: 3;
    }

    Input {
        margin: 1 0;
    }

    #buttons {
        width: 100%;
        height: 3;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }
    """
