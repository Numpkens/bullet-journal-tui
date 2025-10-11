from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header,
    Footer,
    Label,
    Static,
    ListView,
    ListItem,
    Button,
    TextArea,
)
from textual.containers import Container
from datetime import datetime
from typing import List, TYPE_CHECKING 

# Import all entry classes
# Note: 'Signifier' is accessed via the entry object, so it's not needed here directly.
from journal_app.entry import JournalEntry, TaskEntry, NoteEntry 

# CRITICAL: Conditional Import for Type Checking to break the circular dependency
if TYPE_CHECKING:
    from journal_app.app import BulletJournalApp


# --- Custom Widget for an Entry ---

class EntryDisplay(Static):
    """A widget to display a single journal entry. (Step 4: Display Symbols)"""
    
    def __init__(self, entry: JournalEntry, **kwargs):
        # Displays the BuJo rapid logging symbol
        display_text = f"[{entry.signifier.value}] {entry.content}" 
        if isinstance(entry, TaskEntry):
            status = f" ({entry.status})"
            display_text += status
        
        timestamp_str = entry.timestamp.strftime("%Y-%m-%d %H:%M")
        display_text += f" [dim]{timestamp_str}[/]"

        super().__init__(display_text, **kwargs)
        self.entry = entry

# --- Screens ---

class JournalScreen(Screen['BulletJournalApp']):
    """The main screen to view all journal entries. (Step 1 Fix)"""

    BINDINGS = [
        ("n", "push_screen('new_entry')", "New Entry"), 
        ("q", "quit", "Quit"),
        # (Step 6: Add Log/Filter bindings here later)
    ]

    def __init__(self, entries: List[JournalEntry], **kwargs):
        super().__init__(**kwargs)
        self.entries = entries

    def compose(self) -> ComposeResult:
        """Composes the main journal view."""
        yield Label("Journal Log", id="journal-title")
        yield ListView(
            # 💥 FIX: This list comprehension ensures the ListView is populated
            *(ListItem(EntryDisplay(entry, classes=entry.type.lower())) for entry in self.entries),
            id="entry-list"
        )
    
    async def action_quit(self):
        await self.app.action_quit() 
        
    def action_push_screen(self, screen_name: str):
        self.app.push_screen(screen_name)


class NewEntryScreen(Screen['BulletJournalApp']): 
    """A screen used for creating a new journal entry. (Step 3: Redesign for types)"""
    
    BINDINGS = [
        ("escape", "pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        # Placeholder for Step 3: We will replace this simple form with a complex one.
        yield Header()
        yield Footer()
        
        yield Container(
            Label("New Journal Entry", id="new-entry-title"),
            TextArea(
                placeholder="What's on your mind? (Defaulting to Note)",
                id="entry-content-input"
            ),
            Button("Submit Entry", variant="success", id="submit-button"),
            id="new-entry-form"
        )

    def action_pop_screen(self):
        self.app.pop_screen()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles the submission of a new entry."""
        if event.button.id == "submit-button":
            try:
                text_area = self.query_one("#entry-content-input", TextArea)
            except Exception:
                return
                
            content = text_area.text.strip()
            
            if not content:
                return

            # Note: This hardcoded NoteEntry will be replaced in Step 3
            new_entry = NoteEntry(content=content, timestamp=datetime.now())
            
            self.app.entries.append(new_entry) # type: ignore 
            
            self.action_pop_screen()
