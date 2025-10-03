# 1. this code should import dataclass, datetime and enum 
# 2. should have an enum "signifier " and it should contain members like priority, inspiration, and none
# 3. should have a journal entry baseclass including an auto generated  date time stamp default_factory=
# 4. create a specialized taskentry class(it will set its typ to task and adds the pending status by default)

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







