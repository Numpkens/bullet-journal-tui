from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header,
    Footer,
    Label,
    Static,
    ListView,
    ListItem,
    Select,
    Button,
    TextArea,
)
# NOTE: Added Horizontal to containers import
from textual.containers import Container, Horizontal 
from datetime import datetime
from typing import List, TYPE_CHECKING
from journal_app.entry import JournalEntry, TaskEntry, Signifier, NoteEntry, EventEntry, HabitEntry 

if TYPE_CHECKING:
    from journal_app.app import BulletJournalApp


# --- Helper Widget for displaying an entry in the list ---
class EntryDisplay(Static):
    """A static widget to display a single JournalEntry's content."""
    
    def __init__(self, entry: JournalEntry, **kwargs):
        super().__init__(self._get_display_text(entry), **kwargs)
        self.add_class(entry.type.lower()) 

    def _get_display_text(self, entry: JournalEntry) -> str:
        """Formats the journal entry content for display."""
        
        # Default format
        timestamp = entry.timestamp.strftime('%H:%M')
        signifier = entry.signifier.value
        text = f"[{timestamp}] {signifier} {entry.content}"
        
        # Task specific formatting
        if isinstance(entry, TaskEntry):
            # Using simple symbols for tasks
            symbol = "✗" if entry.status == "Complete" else ("→" if entry.status == "Migrated" else "•")
            return f"[{timestamp}] {symbol}{entry.signifier.value} {entry.content} ({entry.status})"
        
        # Event specific formatting (using the original logic)
        if isinstance(entry, EventEntry) and entry.location:
            return f"{text} @ {entry.location}"
        
        return text


# --- Journal Log Screen (FIXED to display entries and composition) ---

class JournalScreen(Screen['BulletJournalApp']):
    """The main display screen for all journal entries."""
    
    def __init__(self, entries: List[JournalEntry], **kwargs):
        """Initializes the screen and stores the list of entries."""
        super().__init__(**kwargs)
        self.entries = entries 
        # Initial sort (most recent first)
        self.entries.sort(key=lambda e: e.timestamp, reverse=True) 

    def _create_list_items(self) -> List[ListItem]:
        """Helper to convert JournalEntry list to ListItem/EntryDisplay list."""
        # The EntryDisplay widget is wrapped in a ListItem for use in ListView
        return [ListItem(EntryDisplay(entry)) for entry in self.entries]

    def compose(self) -> ComposeResult:
        """Composes the widgets for the screen."""
        yield Header()
        yield Footer()
        
        yield Static("DAILY LOG", id="journal-title")
        
        # --- Future Log Filter Container (Composed without internal query) ---
        with Container(id="future-log-filters"):
            # YIELD the widgets here. Do NOT use self.query_one inside compose.
            yield Label("Future Log Filter", id="filter-title")
            with Horizontal(id="filter-controls"):
                # Using empty options list for now, as per the trace context
                yield Select(options=[], prompt="Select Year", id="filter-year-select")
                yield Select(options=[], prompt="Select Month", id="filter-month-select")

        # The ListView is populated with the initial set of list items
        yield ListView(*self._create_list_items(), id="entry-list")

    def on_mount(self) -> None:
        """
        Runs once after the widgets are composed and the screen is attached.
        Used here to hide the Future Log Filter container safely.
        """
        # CRITICAL FIX: Hide the container here, AFTER it has been composed/mounted.
        try:
            self.query_one("#future-log-filters", Container).display = False
        except Exception:
            # Fallback to prevent crashing if the widget ID is changed later
            pass

    def update_list(self) -> None:
        """
        Refreshes the entry list on the screen.
        Called by NewEntryScreen after a new entry is added.
        """
        self.entries.sort(key=lambda e: e.timestamp, reverse=True)
        
        list_view = self.query_one("#entry-list", ListView)

        list_view.clear()
        
        for item in self._create_list_items():
            list_view.append(item)


# --- New Entry Screen (Simplified options to avoid 'Option' import error) ---

class NewEntryScreen(Screen['BulletJournalApp']):
    """A screen used for creating a new journal entry."""
    
    BINDINGS = [
        ("escape", "pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        """Composes the form widgets."""
        yield Header()
        yield Footer()

        # The Container centers and contains the entire form
        with Container(id="new-entry-form"):
            yield Label("Add New Journal Entry", classes="form-title")

            # 1. Entry Type Select (Using tuples for options)
            yield Select(
                [
                    ("Note", "note"), 
                    ("Task", "task"), 
                    ("Event", "event"),
                ],
                prompt="Select Entry Type",
                value="note",
                id="entry-type-select",
            )
            
            # 2. Signifier Select (Using tuples for options)
            yield Select(
                [
                    (f"Priority ({Signifier.PRIORITY.value})", Signifier.PRIORITY.value),
                    (f"Inspiration ({Signifier.INSPIRATION.value})", Signifier.INSPIRATION.value),
                    ("None", Signifier.NONE.value),
                ],
                prompt="Select Signifier",
                value=Signifier.NONE.value,
                id="signifier-select",
            )
            
            # 3. Task Status (Conditional Field - Using tuples for options)
            yield Select(
                [
                    ("Pending", "Pending"), 
                    ("Complete", "Complete"), 
                    ("Migrated", "Migrated"),
                ],
                prompt="Task Status",
                value="Pending",
                id="task-status-select",
            )

            # 4. Content Area
            yield Label("Content:", classes="input-label")
            yield TextArea(id="content-input")

            # 5. Submit Button
            yield Button("Create Entry", variant="primary", id="submit-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles the 'Create Entry' button press."""
        if event.button.id == "submit-button":
            # Get values from the form
            entry_type = self.query_one("#entry-type-select", Select).value
            signifier_value = self.query_one("#signifier-select", Select).value
            content = self.query_one("#content-input", TextArea).text.strip()
            task_status = self.query_one("#task-status-select", Select).value
            
            if not content:
                return

            # Convert signifier value back to Enum
            signifier = next((s for s in Signifier if s.value == signifier_value), Signifier.NONE)
            
            # Create the correct entry object
            if entry_type == "task":
                new_entry = TaskEntry(
                    content=content, 
                    signifier=signifier, 
                    status=str(task_status),
                    timestamp=datetime.now()
                )
            # Default to NoteEntry for simplicity/flexibility
            else:
                new_entry = NoteEntry(
                    content=content, 
                    signifier=signifier, 
                    timestamp=datetime.now()
                )

            # Add the new entry to the app state
            self.app.entries.append(new_entry) # type: ignore 
            
            # Update list on JournalScreen before popping
            journal_screen_instance = self.app.query_one("#journal", JournalScreen)
            journal_screen_instance.update_list() 

            self.action_pop_screen()

    def action_pop_screen(self):
        """Pops the current screen off the stack."""
        self.app.pop_screen()
