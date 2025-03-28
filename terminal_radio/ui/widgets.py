from textual.widget import Widget
from textual.reactive import Reactive
from textual.containers import Container
from textual.widgets import Button, ProgressBar


class VolumeControl(Widget):
    volume: Reactive[int] = Reactive(50)  # Default volume set to 50%

    def render(self) -> Container:
        return Container(
            ProgressBar(value=self.volume, min=0, max=100, label="Volume"),
            Button(label="Mute", on_click=self.mute),
            Button(label="Unmute", on_click=self.unmute),
        )

    def mute(self) -> None:
        self.volume = 0

    def unmute(self) -> None:
        self.volume = 50  # Reset to default volume
