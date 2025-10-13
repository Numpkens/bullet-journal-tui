from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List

class Signifier(Enum):
    """Ryder Carroll Bullet Journal Signifiers"""
    PRIORITY = "*"      # Priority
    INSPIRATION = "!"   # Inspiration/Ideas
    EXPLORE = "?"       # Questions to explore
    NONE = ""          # No signifier

class TaskStatus(Enum):
    """Ryder Carroll Bullet Journal Task States"""
    INCOMPLETE = "•"    # Task (incomplete)
    COMPLETE = "×"      # Task (complete)
    MIGRATED = ">"      # Task (migrated to new month)
    SCHEDULED = "<"     # Task (scheduled for future)
    IRRELEVANT = "−"    # Task (struck through/irrelevant)

@dataclass
class JournalEntry:
    """Base class for all journal entries"""
    content: str
    type: str
    signifier: Signifier = Signifier.NONE
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_date_str(self) -> str:
        """Returns formatted date string"""
        return self.timestamp.strftime('%m/%d/%Y')
    
    def get_time_str(self) -> str:
        """Returns formatted time string"""
        return self.timestamp.strftime('%I:%M %p')

@dataclass
class NoteEntry(JournalEntry):
    """Simple note or thought."""
    type: str = field(default="Note", init=False)

@dataclass
class TaskEntry(JournalEntry):
    """An action that needs to be taken."""
    status: TaskStatus = TaskStatus.INCOMPLETE
    type: str = field(default="Task", init=False)
    
    def complete(self):
        """Mark task as complete."""
        self.status = TaskStatus.COMPLETE
    
    def migrate(self):
        """Mark task as migrated."""
        self.status = TaskStatus.MIGRATED

@dataclass
class EventEntry(JournalEntry):
    """A scheduled event or appointment."""
    location: Optional[str] = None
    type: str = field(default="Event", init=False)
    # NEW: Allow events to be marked as completed/past
    is_completed: bool = False 

    def complete(self):
        """Mark event as completed/past."""
        self.is_completed = True

@dataclass
class HabitEntry(JournalEntry):
    """A habit to be tracked daily."""
    frequency: str = "Daily"
    type: str = field(default="Habit", init=False)
    # Stores dates when completed (YYYY-MM-DD format)
    completed_dates: List[str] = field(default_factory=list) 
    
    def mark_complete(self, completion_date: Optional[date] = None):
        """Mark habit as completed for a specific date (defaults to today)."""
        if completion_date is None:
            completion_date = date.today()
        
        date_str = completion_date.isoformat()
        if date_str not in self.completed_dates:
            self.completed_dates.append(date_str)
            self.completed_dates.sort(reverse=True)
    
    def is_completed_today(self) -> bool:
        """Check if habit was completed today."""
        today = date.today().isoformat()
        return today in self.completed_dates
    
    def get_completion_count(self, start_date: date, end_date: date) -> int:
        """Get number of completions in a date range"""
        return sum(
            1 for date_str in self.completed_dates
            if start_date.isoformat() <= date_str <= end_date.isoformat()
        )
    
    def get_streak(self) -> int:
        """Calculate current streak of consecutive days"""
        if not self.completed_dates:
            return 0
        
        sorted_dates = sorted([date.fromisoformat(d) for d in self.completed_dates], reverse=True)
        
        streak = 0
        expected_date = date.today()
        
        for completed in sorted_dates:
            if completed == expected_date:
                streak += 1
                expected_date = date.fromordinal(expected_date.toordinal() - 1)
            elif completed < expected_date:
                if completed != date.fromordinal(expected_date.toordinal() - 1):
                    break
                streak += 1
                expected_date = date.fromordinal(expected_date.toordinal() - 1)
        return streak
