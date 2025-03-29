from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Horizontal, Vertical


class ConfirmDeleteScreen(ModalScreen):
    """Confirmation dialog for station deletion."""

    def __init__(self, station, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.station = station

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"Delete station '{self.station.name}'?", id="confirm-title"),
            Horizontal(
                Button("Yes", variant="error", id="confirm"),
                Button("No", variant="primary", id="cancel"),
                id="confirm-buttons",
            ),
            id="confirm-dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "confirm":
            self.app.station_controller.delete_station(self.station.id)
            self.app.main_screen.update_status(f"Station '{self.station.name}' deleted")
            self.app.main_screen.query_one(f"#station-{self.station.id}").remove()
            self.station = None
        self.app.pop_screen()

    def key_escape(self) -> None:
        """Handle escape key press."""
        self.app.pop_screen()

    CSS = """
    #confirm-dialog {
        background: $surface;
        padding: 1;
        width: 50;
        height: auto;
        border: thick $error;
        margin: 1 2;
    }

    #confirm-title {
        text-align: center;
        height: 3;
    }

    #confirm-buttons {
        width: 100%;
        height: 3;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }
    """
