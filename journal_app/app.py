from journal_app.persistence import FileJournalRepository
from journal_app.entry import (
    JournalEntry, NoteEntry, TaskEntry, EventEntry, HabitEntry,
    Signifier, TaskStatus
)
from datetime import datetime, date, timedelta
from typing import List, Type # <--- FIXED: changed 'type' to 'Type'
import sys 
import calendar # For monthly view
from tabulate import tabulate # <--- ADDED IMPORT

# =========================================================================
# APPLICATION CORE
# =========================================================================

class BulletJournalCLI:
    """Core logic and CLI controller for the Bullet Journal application."""
    
    def __init__(self, repository=None):
        self.repository = repository or FileJournalRepository()
        self.entries: list[JournalEntry] = self.repository.load_entries()
        
        if not self.entries:
            self.entries = self._create_sample_entries()
        
        self._sort_entries()

    def _create_sample_entries(self) -> List[JournalEntry]:
        """Creates instructional placeholder entries for a new journal."""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        return [
            NoteEntry(
                content="Welcome to your CLI Bullet Journal! Start by pressing 'A' to Add an entry.",
                signifier=Signifier.INSPIRATION, # !
                timestamp=today
            ),
            TaskEntry(
                content="Task: Press 'X' or 'M' and the index number to mark me as Complete (X) or Migrated (>).",
                status=TaskStatus.INCOMPLETE,
                signifier=Signifier.PRIORITY, # *
                timestamp=today
            ),
            EventEntry(
                content="Event: Press 'C' and the index number to mark me as Complete (✓).",
                location="Demo Location",
                signifier=Signifier.NONE, # O
                timestamp=today
            ),
            HabitEntry(
                content="Habit: Press 'H' and the index number to mark me as complete for TODAY.",
                frequency="Daily",
                signifier=Signifier.NONE, # ◷
                timestamp=yesterday, # Give it an older timestamp so it appears later in the list
                completed_dates=[]
            ),
            NoteEntry(
                content="View your Spreads: Press 'V' to see the Weekly, Monthly, and Habit Tracker views.",
                signifier=Signifier.EXPLORE, # ?
                timestamp=yesterday - timedelta(hours=1)
            ),
        ]
    def _sort_entries(self) -> None:
        """Sorts entries by timestamp"""
        self.entries.sort(key=lambda e: e.timestamp, reverse=True)

    def _format_entry(self, entry: JournalEntry, index: int) -> str:
        """Formats a single entry for CLI output."""
        
        date_str = entry.timestamp.strftime('%Y-%m-%d')
        time_str = entry.timestamp.strftime('%H:%M')
        signifier = entry.signifier.value if entry.signifier.value else " "
        content = entry.content
        symbol = " " 
        entry_type = entry.type
        
        if isinstance(entry, TaskEntry):
            symbol = entry.status.value
            
        elif isinstance(entry, EventEntry):
            # NEW: Check completion status
            symbol = "✓" if entry.is_completed else "○" 
            content += f" @ {entry.location}" if entry.location else ""
        
        elif isinstance(entry, HabitEntry):
            # Show checkmark if completed today, otherwise show habit symbol
            symbol = "✓" if entry.is_completed_today() else "◷" 
            
        else: # NoteEntry
            symbol = "−"
            
        # Format: [Index] [Date] [Time] [Symbol][Signifier] Content
        return f"[{index:02}] {date_str} {time_str} {symbol}{signifier} {content} ({entry_type})"

    def _get_simple_symbol(self, entry: JournalEntry) -> str:
        """Helper to get only the core symbol for spreads."""
        if isinstance(entry, TaskEntry):
            return entry.status.value
        elif isinstance(entry, EventEntry):
            return "✓" if entry.is_completed else "○" 
        elif isinstance(entry, HabitEntry):
            return "✓" if entry.is_completed_today() else "◷"
        else:
            return "−"

    # --- CLI Loop & Menu ---
    
    # ... (run, display_journal, _display_menu methods are unchanged)
    def run(self):
        """Starts the main CLI loop."""
        print("\n **CLI BULLET JOURNAL**\n")
        
        while True:
            self._sort_entries()
            self.display_journal()
            
            action = self._display_menu()
            
            if action == 'Q':
                self.quit_app()
            elif action == 'A':
                self.add_entry()
            elif action == 'X':
                self.complete_task()
            elif action == 'M':
                self.migrate_task()
            elif action == 'H':
                self.mark_habit_complete()
            # NEW ACTIONS
            elif action == 'C':
                self.complete_event()
            elif action == 'V':
                self.view_spreads()
            else:
                print("Invalid action. Please try again.")

    def display_journal(self):
        """Prints the entire journal to the console."""
        print("-" * 50)
        print("JOURNAL ENTRIES (Sorted by date, newest first):")
        if not self.entries:
            print("  No entries yet. Press 'A' to add one.")
        else:
            for i, entry in enumerate(self.entries):
                print(self._format_entry(entry, i + 1))
        print("-" * 50)

    def _display_menu(self) -> str:
        """Prints the menu and gets user input."""
        print("\nActions: [A]dd | [X] Complete Task | [M] Migrate Task | [H] Complete Habit | [C] Complete Event | [V] View Spreads | [Q]uit")
        user_input = input("Enter action: ").strip().upper()
        return user_input

    def add_entry(self):
        """CLI prompts to create a new entry."""
        print("\n--- NEW ENTRY ---")
        
        entry_type = input("Type ([N]ote, [T]ask, [E]vent, [H]abit): ").strip().upper()
        
        if entry_type not in ('N', 'T', 'E', 'H'):
            print("Invalid type. Returning to main menu.")
            return

        content = input("Content: ").strip()
        if not content:
            print("Content cannot be empty. Returning to main menu.")
            return
            
        sig_input = input("Signifier (*, !, ? or [Enter] for None): ").strip()
        signifier = next(
            (s for s in Signifier if s.value == sig_input), 
            Signifier.NONE
        )

        new_entry = None
        
        if entry_type == 'N':
            new_entry = NoteEntry(content=content, signifier=signifier)
        
        elif entry_type == 'T':
            new_entry = TaskEntry(content=content, signifier=signifier, status=TaskStatus.INCOMPLETE)
            
        elif entry_type == 'E':
            location = input("Location (Optional): ").strip()
            new_entry = EventEntry(content=content, signifier=signifier, location=location or None)
        
        elif entry_type == 'H':
            frequency = input("Frequency (e.g., Daily, Weekly): ").strip()
            new_entry = HabitEntry(content=content, signifier=signifier, frequency=frequency)

        if new_entry:
            self.entries.append(new_entry)
            print("Entry added successfully!")

    def _get_entry_by_index(self, prompt: str, required_type: Type) -> JournalEntry | None: # <--- FIXED: changed 'type' to 'Type'
        """Helper to get a specific entry type via index validation."""
        try:
            index_input = input(prompt).strip()
            index = int(index_input) - 1
            
            if 0 <= index < len(self.entries):
                entry = self.entries[index]
                if isinstance(entry, required_type):
                    return entry
                else:
                    entry_name = entry.type
                    if not entry_name: 
                         entry_name = required_type.__name__.replace('Entry', '')
                    
                    print(f"Entry {index + 1} is a {entry_name}, not a {required_type.__name__.replace('Entry', '')}.")
                    return None
            else:
                print("Invalid index.")
                return None
        except ValueError:
            print("Invalid input. Please enter a number.")
            return None


    def complete_task(self):
        """Marks a selected task as complete."""
        entry = self._get_entry_by_index("Enter index of Task to [X] Complete: ", TaskEntry)
        if entry:
            entry.complete()
            print(f"Task '{entry.content}' marked as {entry.status.name} (×).")

    def migrate_task(self):
        """Marks a selected task as migrated."""
        entry = self._get_entry_by_index("Enter index of Task to [M] Migrate: ", TaskEntry)
        if entry:
            entry.migrate()
            print(f"Task '{entry.content}' marked as {entry.status.name} (>).")

    def mark_habit_complete(self):
        """Marks a selected habit as complete for today."""
        entry = self._get_entry_by_index("Enter index of Habit to [H] Complete for Today: ", HabitEntry)
        if entry:
            entry.mark_complete()
            print(f"Habit '{entry.content}' marked as complete for today (✓).")

    def complete_event(self):
        """Marks a selected event as complete."""
        entry = self._get_entry_by_index("Enter index of Event to [C] Complete: ", EventEntry)
        if entry:
            entry.complete()
            print(f"Event '{entry.content}' marked as complete (✓).")

    def view_spreads(self):
        """Shows sub-menu for different calendar views/spreads."""
        print("\n--- VIEW SPREADS ---")
        while True:
            print("Views: [H]abits | [W]eekly | [M]onthly | [B]ack to Journal")
            view_action = input("Enter view: ").strip().upper()

            if view_action == 'H':
                self.display_habit_spread()
            elif view_action == 'W':
                self.display_weekly_view()
            elif view_action == 'M':
                self.display_monthly_view()
            elif view_action == 'B':
                return
            else:
                print("Invalid view option.")

    def display_habit_spread(self):
        """Displays a table showing habit completion for the last 7 days."""
        print("\n--- HABIT TRACKER SPREAD ---")
        habit_entries = [e for e in self.entries if isinstance(e, HabitEntry)]
        
        if not habit_entries:
            print("No habit entries found.")
            input("Press Enter to continue...")
            return

        # Define the 7-day date range (Today and the 6 previous days)
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(7)][::-1] # Last 7 days, oldest first
        
        # Setup the table header
        headers = ["Habit"] + [d.strftime('%a %d') for d in dates]

        # Fill the table rows
        table_data = []
        for habit in habit_entries:
            row = [habit.content]
            
            for d in dates:
                is_done = d.isoformat() in habit.completed_dates
                # Use '+' as requested in the initial requirements for completion
                row.append("+" if is_done else " ") 
            
            table_data.append(row)

        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid")) # <--- USING TABULATE
        input("Press Enter to continue...") # Pause for viewing

    def display_weekly_view(self):
        """Filters and displays entries for the current week using tabulate."""
        print("\n--- WEEKLY SPREAD ---")
        today = datetime.now().date()
        # Find the start of the week (Monday)
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        print(f"Showing entries for: {start_of_week.strftime('%Y-%m-%d')} to {end_of_week.strftime('%Y-%m-%d')}")
        
        # Sort by date (oldest first) before filtering
        all_entries_sorted = sorted(self.entries, key=lambda e: e.timestamp)
        
        filtered_entries = [
            e for e in all_entries_sorted 
            if start_of_week <= e.timestamp.date() <= end_of_week
        ]
        
        if not filtered_entries:
            print("No entries found for this week.")
        else:
            table_data = []
            for entry in filtered_entries:
                symbol = self._get_simple_symbol(entry)
                signifier = entry.signifier.value if entry.signifier.value else ""
                
                table_data.append([
                    entry.timestamp.strftime('%a %d'),
                    entry.timestamp.strftime('%H:%M'),
                    f"{symbol}{signifier}",
                    entry.content
                ])

            print(tabulate(table_data, headers=["Day", "Time", "Sym", "Entry"], tablefmt="grid")) # <--- USING TABULATE

        input("Press Enter to continue...")

    def display_monthly_view(self):
        """Filters and displays entries for the current month using tabulate."""
        print("\n--- MONTHLY SPREAD ---")
        now = datetime.now()
        year = now.year
        month = now.month
        
        # Determine the range for the current month
        _, last_day = calendar.monthrange(year, month)
        start_of_month = date(year, month, 1)
        end_of_month = date(year, month, last_day)

        print(f"Showing entries for: {start_of_month.strftime('%B %Y')}")
        
        # Sort by date (oldest first) before filtering
        all_entries_sorted = sorted(self.entries, key=lambda e: e.timestamp)
        
        filtered_entries = [
            e for e in all_entries_sorted 
            if start_of_month <= e.timestamp.date() <= end_of_month
        ]
        
        # Print the calendar grid
        cal_str = calendar.month(year, month)
        print(cal_str)
        
        if not filtered_entries:
            print("-" * 20)
            print("No entries found for this month.")
        else:
            # Group entries by day of the month for better organization
            daily_entries = {}
            for entry in filtered_entries:
                day = entry.timestamp.day
                if day not in daily_entries:
                    daily_entries[day] = []
                daily_entries[day].append(entry)

            print("-" * 20)
            
            table_data = []
            for day in sorted(daily_entries.keys()):
                
                # Combine all entries for a given day into one or more rows
                for i, entry in enumerate(daily_entries[day]):
                    symbol = self._get_simple_symbol(entry)
                    signifier = entry.signifier.value if entry.signifier.value else ""
                    
                    # Only show the day number once per day group
                    day_str = f"DAY {day:02}" if i == 0 else "" 
                    
                    table_data.append([
                        day_str,
                        entry.timestamp.strftime('%H:%M'),
                        f"{symbol}{signifier}",
                        entry.content
                    ])
            
            print(tabulate(table_data, headers=["Day", "Time", "Sym", "Entry"], tablefmt="grid")) # <--- USING TABULATE
        
        input("Press Enter to continue...")

    def quit_app(self):
        """Quit the application and save data"""
        self.repository.save_entries(self.entries)
        print("\nJournal saved. Goodbye! 👋")
        sys.exit(0)

# =========================================================================
# ENTRY POINT
# =========================================================================

if __name__ == "__main__":
    app = BulletJournalCLI()
    app.run()
