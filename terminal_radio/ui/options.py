from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select
from textual.containers import Horizontal, Vertical
from textual.theme import BUILTIN_THEMES
from terminal_radio.controllers.options import OptionsController
from terminal_radio.events.config import ConfigUpdated


class OptionsScreen(ModalScreen):
    """Screen for adding a new station."""

    CONFIG_UPDATED_EVENT = ConfigUpdated

    def __init__(self, *args, options_controller: OptionsController, **kwargs):
        super().__init__(*args, **kwargs)
        self.options_controller = options_controller

    def compose(self) -> ComposeResult:
        device_options = self.options_controller.get_available_devices()
        current_device = self.options_controller.options.output_device
        layout = Vertical(
            Vertical(
                Horizontal(
                    Label("Output Device"),
                    Select(
                        device_options,
                        prompt="Output Device"
                        if device_options
                        else "No output devices available",
                        classes="config-part",
                        name="output_device",
                        value=current_device
                        if current_device is not None
                        else Select.BLANK,
                        disabled=not device_options,
                    ),
                    classes="button-box",
                ),
                Horizontal(
                    Label("Theme"),
                    Select(
                        [(v, v) for v in BUILTIN_THEMES],
                        name="theme",
                        value=self.options_controller.options.theme,
                        classes="config-part",
                    ),
                    classes="button-box",
                ),
            ),
            Horizontal(
                Button("Save", variant="success", id="save"),
                Button("Close", variant="error", id="close"),
                id="buttons",
            ),
            id="options-dialog",
        )
        layout.border_title = "Options"
        yield layout

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save":
            config_parts = self.query(".config-part").results()
            self.options_controller.update_options(
                **{c.name: c.value or None for c in config_parts}
            )
            self.app.post_message(self.CONFIG_UPDATED_EVENT())
            self.app.notify(
                "Options saved successfully",
                title="Success",
                severity="information",
            )
        if event.button.id == "close":
            self.key_escape()

    def key_escape(self) -> None:
        """Handle escape key press."""
        self.app.pop_screen()

    CSS = """
    #options-dialog {
        background: $surface;
        width: auto;
        border: solid $accent;
        padding: 1 1;
    }

    #title {
        text-align: center;
        height: 2;
        margin: 1;
    }

    .button-box {
        height: 3;
        content-align: center middle;
        margin: 1 1;
    }
    .button-box > Label {
        height: 3;
        content-align: left middle;
        width: 20;
    }
    .button-box > Select {
        height: 3;
        content-align: center middle;
        box-sizing: border-box;
    }
    #buttons {
        width: 100%;
        align: center bottom;
    }

    Button {
        height: 3;
        width: auto;
        margin: 1 1;
    }

    """
