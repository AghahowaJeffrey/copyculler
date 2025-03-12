from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Footer, Header, Button, Input

class Copyculler(App):
    """A RAG chatbot that lives in the terminal"""
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app"""
        yield Header()
        yield InputSection()
        yield Footer()
        

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


class InputSection(HorizontalGroup):
    """The user input widget"""

    def compose(self) -> ComposeResult:
        """Create child widgets input section"""
        print('working')
        yield HorizontalGroup(Input(placeholder="Enter your message.",
                                    type="text",
                                    name="message",
                                    id="input-message"))

if __name__ == "__main__":
    app = Copyculler()
    app.run()
