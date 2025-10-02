from textual.app import App
from textual.app_test import AppTest
# Import your app class
from journal_app.app import BulletJournalApp

# 💡 Metacognitive Tip:
# AppTest is a *synchronous* testing utility that runs the app in a virtual terminal,
# allowing you to test how your app's state and widgets change without needing a real terminal.

async def test_app_starts_and_has_widgets():
    """Test that the app composes the essential widgets (Header, Footer, Container)."""
    # Create an AppTest instance for your application
    app_test = AppTest(BulletJournalApp)

    # Run the app until the compose method has finished and the initial screen is mounted
    # This is an asynchronous operation, hence 'await'
    await app_test.compose()

    # Assertions: Check if the key widgets are present in the DOM (Document Object Model)
    # The .query() method is a powerful way to check for widgets and their structure.
    assert app_test.app.query_one("Header")
    assert app_test.app.query_one("Footer")
    assert app_test.app.query_one("#app-grid") # Check for the main container by its ID
    assert app_test.app.query_one("#welcome-message") # Check for the welcome label
