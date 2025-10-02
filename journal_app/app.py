from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label
from textual.containers import Container

# 💡 Metacognitive Tip:
# The `ComposeResult` type hint and the `compose` method are core Textual patterns.
# The `compose` method is how you define the initial layout of your app's screen.

class BulletJournalApp(App):
    """The main Textual application for the Rider Carroll-style Bullet Journal."""

    # Set the CSS file for styling
    CSS_PATH = "app.css"

    def compose(self) -> ComposeResult:
        """Create a header, footer, and a main content area."""
        yield Header()
        yield Footer()
        # This will be the main area where you display the journal content
        yield Container(
            Label("Welcome to your Bullet Journal!", id="welcome-message"),
            id="app-grid"
        )

# This block allows you to run the app directly
if __name__ == "__main__":
    app = BulletJournalApp()
    app.run()
