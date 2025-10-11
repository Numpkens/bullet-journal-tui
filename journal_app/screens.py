from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header,
    Footer,
    Label,
    Input,
    Select,
    Button,
    TextArea,
    Static,
    ListView,
    ListItem,
)
# 💥 CRITICAL FIX: The correct path for the Option class
from textual.widgets.select import Option
from textual.containers import Container, Horizontal
from datetime import datetime
from typing import List, TYPE_CHECKING
from journal_app.entry import JournalEntry, TaskEntry, Signifier, NoteEntry, EventEntry 

if TYPE_CHECKING:
    from journal_app.app import BulletJournalApp


# --- Helper Widget for displaying an entry in the list (Required by JournalScreen) ---
class EntryDisplay(Static):
    """A static widget to display a single JournalEntry's content."""
    
    def __init__(self, entry: JournalEntry, **kwargs):
        super().__init__(self._get_display_text(entry), **kwargs)
        self.add_class(entry.type.lower()) 

    def _get_display_text(self, entry: JournalEntry) -> str:
        text = f"[{entry.timestamp.strftime('%H:%M')}] {entry.signifier.value} {entry.content}"
        
        if isinstance(entry, TaskEntry):
            symbol = "✗" if entry.status == "Complete" else (">" if entry.status == "Migrated" else "•")
            return f"[{entry.timestamp.strftime('%H:%M')}] {symbol}{entry.signifier.value} {entry.content} ({entry.status})"
        
        if isinstance(entry, EventEntry) and entry.location:
            return f"{text} @ {entry.location}"

        return text

# --- Main Journal Screen (Required by app.py) ---
class JournalScreen(Screen['BulletJournalApp']):
    """The main screen displaying the journal entries with filtering."""
    
    BINDINGS = [
        ("n", "push_screen('new_entry')", "New Entry"),
        ("x", "complete_task", "Complete Task (x)"), 
        ("m", "migrate_task", "Migrate Task (m)"),   
        ("f", "toggle_filter_view", "Future Log Filter"), 
        ("q", "quit", "Quit"),
    ]

    def __init__(self, entries: List[JournalEntry], **kwargs):
        super().__init__(**kwargs)
        self.entries = entries

    def compose(self) -> ComposeResult:
        yield Label("Journal Log", id="journal-title")
        
        # Future Log Filter Container
        with Container(id="future-log-filters", visible=False): 
            yield Label("Future Log Filter", id="filter-title")
            with Horizontal(id="filter-controls"):
                yield Select(options=[], prompt="Select Year", id="filter-year-select")
                yield Select(options=[], prompt="Select Month", id="filter-month-select")
                yield Button("Apply Filter", id="apply-filter-button", variant="primary")
        
        yield ListView(id="entry-list")
        
    def on_mount(self) -> None:
        self.update_list()
        self._populate_filter_options()

    def _populate_filter_options(self) -> None:
        years = set()
        for entry in self.entries:
            years.add(entry.timestamp.year)

        year_options = [Option(str(y), y) for y in sorted(list(years), reverse=True)]
        year_options.insert(0, Option("All Years", 0, default=True))
        
        month_map = {i: datetime(2000, i, 1).strftime('%B') for i in range(1, 13)}
        month_options = [Option(name, i) for i, name in month_map.items()]
        month_options.insert(0, Option("All Months", 0, default=True))

        self.query_one("#filter-year-select", Select).options = year_options # type: ignore
        self.query_one("#filter-month-select", Select).options = month_options # type: ignore
        
    def action_toggle_filter_view(self) -> None:
        filter_container = self.query_one("#future-log-filters", Container)
        filter_container.visible = not filter_container.visible
        
        if not filter_container.visible:
            self.update_list()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "apply-filter-button":
            self.action_filter_log()

    def action_filter_log(self) -> None:
        filter_year = int(self.query_one("#filter-year-select", Select).value)
        filter_month = int(self.query_one("#filter-month-select", Select).value)
        self.update_list(filter_year, filter_month)

    def update_list(self, filter_year: int = 0, filter_month: int = 0) -> None:
        list_view = self.query_one(ListView)
        list_view.clear()
        
        filtered_entries = self.entries
        
        if filter_year != 0:
            filtered_entries = [e for e in filtered_entries if e.timestamp.year == filter_year]
        if filter_month != 0:
            filtered_entries = [e for e in filtered_entries if e.timestamp.month == filter_month]

        sorted_entries = sorted(filtered_entries, key=lambda e: e.timestamp, reverse=True)
        
        for entry in sorted_entries:
            list_view.append(
                ListItem(EntryDisplay(entry))
            )
        
    # Task Action Methods
    def _get_selected_task(self) -> TaskEntry | None:
        list_view = self.query_one(ListView)
        selected_index = list_view.index
        
        if selected_index is None:
            self.notify("Select an item first.", title="Action Failed")
            return None
            
        sorted_entries = sorted(self.entries, key=lambda e: e.timestamp, reverse=True) 
        
        if selected_index >= len(sorted_entries): return None 
        selected_entry = sorted_entries[selected_index]
        
        if not isinstance(selected_entry, TaskEntry):
            self.notify("Action only applies to Task entries.", title="Action Failed")
            return None
        return selected_entry

    def action_complete_task(self) -> None:
        task = self._get_selected_task()
        if task:
            task.status = "Complete"
            self.update_list()
            
    def action_migrate_task(self) -> None:
        task = self._get_selected_task()
        if task:
            task.status = "Migrated"
            self.update_list()
    

# --- New Entry Screen (The content you provided) ---
class NewEntryScreen(Screen['BulletJournalApp']):
    """A screen used for creating a new journal entry."""
    
    BINDINGS = [
        ("escape", "pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        """Composes the form widgets."""
        yield Header()
        yield Footer()

        with Container(id="new-entry-form"):
            yield Label("Add New Journal Entry", classes="form-title")

            yield Select(
                [
                    Option("Note", "note", default=True),
                    Option("Task", "task"),
                    Option("Event", "event"),
                ],
                prompt="Entry Type",
                id="entry-type-select",
            )
            
            yield Select(
                [
                    Option("None", Signifier.NONE.value, default=True),
                    Option("* Priority", Signifier.PRIORITY.value),
                    Option("# Inspiration", Signifier.INSPIRATION.value),
                ],
                prompt="Signifier",
                id="signifier-select",
            )

            # Task Status (Start hidden)
            yield Select(
                [
                    Option("Pending", "Pending", default=True),
                    Option("Complete", "Complete"),
                ],
                prompt="Task Status",
                id="task-status-select",
                classes="hidden", 
            )

            yield TextArea(id="content-input", placeholder="Enter your journal entry content here...")

            yield Button("Add Entry", id="submit-button", variant="primary")

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.control.id == "entry-type-select":
            task_status = self.query_one("#task-status-select")
            if event.value == "task":
                task_status.remove_class("hidden")
            else:
                task_status.add_class("hidden")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit-button":
            entry_type = self.query_one("#entry-type-select", Select).value
            signifier_value = self.query_one("#signifier-select", Select).value
            content = self.query_one("#content-input", TextArea).text.strip()
            task_status = self.query_one("#task-status-select", Select).value
            
            if not content:
                return

            signifier = next((s for s in Signifier if s.value == signifier_value), Signifier.NONE)
            
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

            # Add the new entry to the app state and pop the screen
            self.app.entries.append(new_entry) # type: ignore 
            
            # Update list on JournalScreen before popping
            journal_screen_instance = self.app.query_one("#journal", JournalScreen)
            journal_screen_instance.update_list() 

            self.action_pop_screen()

    def action_pop_screen(self):
        """Pops the current screen off the stack."""
        self.app.pop_screen()
