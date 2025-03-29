import asyncio
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Horizontal, Vertical


class QuitScreen(ModalScreen):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Are you sure you want to quit?", id="question"),
            Horizontal(
                Button("Quit", variant="error", id="quit"),
                Button("Cancel", variant="primary", id="cancel"),
            ),
            id="quit_dialog",
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            try:
                await asyncio.wait_for(self.app.player_controller.cleanup(), timeout=5)
            except asyncio.TimeoutError:
                print("Cleanup took too long, force quitting.")
                self.app.exit(return_code=1)
            self.app.exit()
        else:
            self.app.pop_screen()

    CSS = """

        #quit_dialog {
            background: $surface;
            padding: 1;
            width: 40;
            border: thick $error;
        }

        #question {
            text-align: center;
            height: 3;
            align: center middle;
            margin: 0 1;
        }

        Button {
            margin: 0 1;
        }
        """
