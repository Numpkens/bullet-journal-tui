from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class Signifier(Enum):
    PRIORITY = "*"
    INSPIRATION = "#"
    NONE = " "

@dataclass
class JournalEntry:
    content: str
    type: str
    signifier: Signifier = Signifier.NONE
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class TaskEntry(JournalEntry):
    type: str = "Task"
    status: str = "Pending"

@dataclass
class EventEntry(JournalEntry):
    type: str = "Event"
    location: Optional[str] = None

@dataclass
class NoteEntry(JournalEntry):
    type: str = "Note"

@dataclass
class HabitEntry(JournalEntry):
    type: str = "Habit"
    frequency: str = "Daily"
    progress: list[datetime] = field(default_factory=list)







