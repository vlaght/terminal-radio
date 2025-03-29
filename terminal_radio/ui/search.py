from textual.screen import ModalScreen
from textual.widgets import Input, ListView
from textual.containers import Vertical
from textual.app import ComposeResult
from textual.message import Message
from fuzzywuzzy import fuzz

from terminal_radio.controllers.stations import station_to_dom_node


class SearchScreen(ModalScreen[str]):
    """Modal screen for fuzzy station search."""

    class Selected(Message):
        """Message sent when a station is selected."""

        def __init__(self, *args, station_id: int = 0, **kwargs) -> None:
            self.station_id = station_id
            super().__init__(*args, **kwargs)

    def __init__(self, stations):
        super().__init__()
        self.stations = stations
        self.filtered_stations = stations

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Vertical(
            Input(
                placeholder="Type to search, Esc to close, Enter to select",
                id="search-input",
            ),
            ListView(
                *[station_to_dom_node(s) for s in self.filtered_stations],
                id="search-results",
                initial_index=0,
            ),
            id="search-container",
        )

    def on_mount(self) -> None:
        """Set up initial state."""
        self.query_one("#search-input").focus()

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        await self.update_results(event.value)

    async def update_results(self, query: str) -> None:
        """Update the list of stations based on search query."""
        search_results = self.query_one("#search-results", ListView)
        search_results.clear()
        if not query:
            stations = self.stations
        else:
            stations = [
                s
                for s in sorted(
                    self.stations,
                    key=lambda s: fuzz.ratio(query.lower(), s.name.lower()),
                    reverse=True,
                )
            ][:50]

        await search_results.clear()
        await search_results.extend(
            station_to_dom_node(station) for station in stations
        )
        search_results.index = 0

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle station selection."""
        # message = self.Selected(station_id=event.item.station.id)
        self.app.main_screen.selected_station_by_id(event.item.station.id)
        # posted = self.post_message(message)
        # if posted:
        #     # If the message was posted, close the screen
        self.app.pop_screen()

    def key_escape(self) -> None:
        """Handle escape key press to close the search."""
        self.app.pop_screen()

    def key_down(self) -> None:
        """Handle down arrow key press."""
        search_results = self.query_one("#search-results", ListView)
        search_results.action_cursor_down()

    def key_up(self) -> None:
        """Handle up arrow key press."""
        search_results = self.query_one("#search-results", ListView)
        search_results.action_cursor_up()

    def key_enter(self) -> None:
        """Handle enter key press."""
        search_results = self.query_one("#search-results", ListView)
        if search_results.highlighted_child:
            search_results.action_select_cursor()

    CSS = """
    SearchScreen {
        align: center middle;
    }

    #search-container {
        width: 60;
        height: 20;
        border: thick $accent;
        background: $surface;
        padding: 1;
    }

    #search-input {
        dock: top;
        margin-bottom: 1;
    }

    #search-results {
        height: 1fr;
        border: solid $primary;
        overflow-y: scroll;
    }

    ListItem {
        padding: 0 1;
    }

    ListItem:hover {
        background: $accent;
    }
    """
