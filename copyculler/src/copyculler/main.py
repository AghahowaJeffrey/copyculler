from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Footer, Header

class Copyculler(App):
    """A RAG chatbot that lives in the terminal"""
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app"""
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )



if __name__ == "__main__":
    app = Copyculler()
    app.run()
