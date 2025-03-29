import asyncio
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Horizontal, Vertical, Center


class QuitScreen(ModalScreen):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        yield Vertical(
            Center(Label("Are you sure you want to quit?", id="question")),
            Horizontal(
                Button("Quit", variant="error", id="quit"),
                Button("Cancel", variant="primary", id="cancel"),
                id="buttons",
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
            border: thick $error;
            padding: 1;
            width: 50;
            height: 20;
            margin: 1 2;
        }

        #question {
            height: 3;
            align-vertical: middle;
            align-horizontal: center;
            margin: 1 1;
            padding: 1 1;
        }
        #buttons {
            align: center middle;
        }
        Button {
            height: 3;
            width: auto;
            margin: 1 1;
        }
        """
