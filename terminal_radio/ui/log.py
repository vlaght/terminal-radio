from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Log
from textual.containers import Vertical


class LogScreen(ModalScreen):
    """Screen for editing an existing station."""

    BINDINGS = {
        ("escape", "key_escape", "Close"),
    }

    def __init__(self, log_records: list[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_records = log_records

    def compose(self) -> ComposeResult:
        log = Log(name="log", id="log")
        log.BORDER_TITLE = "Log"
        log.BORDER_SUBTITLE = "Press 'ESC' to close"
        layout = Vertical(
            log,
            id="log-window",
        )
        yield layout

    # def on_ready(self):
    #     log: Log = self.query_one("#log")
    #     log.write_lines(self.log_records)

    def key_escape(self) -> None:
        """Handle escape key press."""
        self.app.pop_screen()

    async def on_mount(self):
        self.query_one("#log", Log).write_lines(self.log_records, scroll_end=True)

    CSS = """
    #log-window {
        background: $surface;
        margin: 1 1;
        height: 95%;
        width: 100%;
    }
    #log {
        background: $surface;
        border: solid $border;
        scrollbar-size: 0 0;
        border-title-align: left;
        border-title-color: $accent;
        border-subtitle-align: left;
        border-subtitle-color: $accent;
        box-sizing: border-box;
        margin: 1 1;
    }
    #footer {
        color: $accent;
    }
    """
