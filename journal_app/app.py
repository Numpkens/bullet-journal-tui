from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

# CRITICAL: Import both screen classes
from journal_app.screens import JournalScreen, NewEntryScreen 
from journal_app.persistence import load_entries, save_entries
from journal_app.entry import JournalEntry, NoteEntry, TaskEntry, Signifier 
from datetime import datetime

class BulletJournalApp(App):
    """The main Textual application for the Rider Carroll-style Bullet Journal."""
    
    CSS_PATH = "app.css"
    
    BINDINGS = [
        ("n", "new_entry", "New Entry"),
        ("q", "quit", "Quit"),
    ]
    
    entries: list[JournalEntry] 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.entries: list[JournalEntry] = load_entries()

        # ✅ FIX: Only add dummy data if the journal is empty
        if not self.entries:
            self.entries = [
                NoteEntry(
                    "Welcome! This is your first entry.", 
                    signifier=Signifier.INSPIRATION, 
                    timestamp=datetime.now()
                ),
                TaskEntry(
                    "Finalize Textual app layout and styles (High Priority).", 
                    status="Pending", 
                    signifier=Signifier.PRIORITY, 
                    timestamp=datetime.now()
                ),
                NoteEntry(
                    "Use 'q' to quit and 'n' to go to the New Entry screen.",
                    timestamp=datetime.now()
                )
            ]
        
        # Install the NewEntryScreen
        self.install_screen(NewEntryScreen(), name="new_entry")

    def compose(self) -> ComposeResult:
        """Composes the application shell (Header/Footer) and the initial screen."""
        yield Header()
        yield Footer()
        
        # Yield the JournalScreen as the initial screen
        yield JournalScreen(self.entries, id="journal")
    
    def action_new_entry(self) -> None:
        """Push the new entry screen."""
        self.push_screen("new_entry")
    
    async def action_quit(self):
        """Quits the application, saving data first."""
        save_entries(self.entries)
        await super().action_quit() 


if __name__ == "__main__":
    app = BulletJournalApp()
    app.run()
