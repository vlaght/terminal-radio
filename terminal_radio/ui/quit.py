import asyncio
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label
from textual.containers import Center


class QuitScreen(Screen):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        yield Center(
            Center(Label("Are you sure you want to quit?", id="question")),
            Center(
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
        QuitScreen {
            align: center middle;
        }
    """
