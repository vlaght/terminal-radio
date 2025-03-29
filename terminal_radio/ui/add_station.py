from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input, ListView
from textual.containers import Horizontal, Vertical
from terminal_radio.controllers.stations import station_to_dom_node


class AddStationScreen(ModalScreen):
    """Screen for adding a new station."""

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Add New Station", id="title"),
            Input(placeholder="Station Name", id="name", value=None, valid_empty=False),
            Input(placeholder="Station URL", id="url", value=None, valid_empty=False),
            Horizontal(
                Button("Save", variant="success", id="save"),
                Button("Cancel", variant="error", id="cancel"),
                id="buttons",
            ),
            id="add-station-dialog",
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save":
            name_input = self.query_one("#name", Input)
            name = name_input.value
            url_input = self.query_one("#url", Input)
            url = url_input.value
            if name and url:
                station = self.app.station_controller.add_station(name, url)
                stations_list: ListView = self.app.main_screen.query_one(
                    "#stations", ListView
                )
                await stations_list.append(station_to_dom_node(station))

                [
                    children.clear()
                    for children in self.query("#add-station-dialog Input")
                ]
                self.query_one("#name", Input).focus()
                self.app.pop_screen()
        else:
            self.app.pop_screen()

    def on_mount(self) -> None:
        """Set focus to the name input field."""
        self.query_one("#name", Input).focus()

    def key_escape(self) -> None:
        """Handle escape key press."""
        self.app.pop_screen()

    CSS = """
    #add-station-dialog {
        background: $surface;
        padding: 1;
        width: 60;
        height: auto;
        border: thick $accent;
        margin: 1 2;
    }

    #title {
        text-align: center;
        height: 2;
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
