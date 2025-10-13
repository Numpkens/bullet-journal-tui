import json
import os
import logging
from datetime import datetime
from enum import Enum
from typing import List, Union, Any, Protocol
from dataclasses import fields as dataclass_fields

from journal_app.entry import (
    Signifier, TaskStatus, # EventSymbol, NoteSymbol, <-- REMOVED THESE
    JournalEntry, TaskEntry, EventEntry, NoteEntry, HabitEntry
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the data file path
DATA_FILE = "journal_data.json"


# ============================================================================
# REPOSITORY PATTERN - Interface Definition
# ============================================================================

class JournalRepository(Protocol):
    """
    Repository interface for journal data persistence.
    """
    
    def load_entries(self) -> List[JournalEntry]:
        """Load all journal entries from storage."""
        ...
    
    def save_entries(self, entries: List[JournalEntry]) -> None:
        """Save all journal entries to storage."""
        ...
    
    def find_by_date_range(self, start: datetime, end: datetime) -> List[JournalEntry]:
        """Find entries within a specific date range."""
        ...


# ============================================================================
# FILE-BASED REPOSITORY IMPLEMENTATION
# ============================================================================

class FileJournalRepository(JournalRepository):
    """Implementation that uses a local JSON file for storage."""
    
    def load_entries(self) -> List[JournalEntry]:
        """Loads entries from the JSON file."""
        entries = []
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    entries = [self._decode_entry(d) for d in data]
                logger.info("Successfully loaded %d entries from %s", len(entries), DATA_FILE)
            except json.JSONDecodeError as e:
                logger.error("Error decoding JSON from %s: %s", DATA_FILE, e)
            except Exception as e:
                logger.error("An unexpected error occurred while loading: %s", e)
        else:
            logger.info("%s not found. Starting with empty journal.", DATA_FILE)
            
        return entries

    def save_entries(self, entries: List[JournalEntry]) -> None:
        """Saves entries to the JSON file."""
        try:
            with open(DATA_FILE, 'w') as f:
                # Use the CustomEncoder for dataclasses and enums
                json.dump(entries, f, indent=4, cls=CustomEncoder)
            logger.info("Successfully saved %d entries to %s", len(entries), DATA_FILE)
        except Exception as e:
            logger.error("Error saving entries to %s: %s", DATA_FILE, e)

    def find_by_date_range(self, start: datetime, end: datetime) -> List[JournalEntry]:
        """Finds entries between start and end dates."""
        all_entries = self.load_entries()
        return [
            entry for entry in all_entries 
            if start <= entry.timestamp <= end
        ]

    # --- Private Decoding Helper ---

    def _decode_entry(self, data: dict) -> JournalEntry:
        """Converts a dictionary back into the appropriate JournalEntry subclass."""
        
        # 1. Extract and remove the type identifier
        entry_type_name = data.pop("_type", "NoteEntry") 
        
        # 2. Decode Enums and Datetime objects
        if 'signifier' in data:
            # Recreate Enum from value
            data['signifier'] = Signifier(data['signifier']) 
        
        if 'status' in data and entry_type_name == 'TaskEntry':
            data['status'] = TaskStatus(data['status'])
        
        if 'timestamp' in data:
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            
        # 3. Handle HabitEntry special case for completion dates (list of strings)
        if entry_type_name == 'HabitEntry' and 'completed_dates' not in data:
            data['completed_dates'] = []

        # 4. Create the correct class instance
        if entry_type_name == 'TaskEntry':
            return TaskEntry(**data)
        elif entry_type_name == 'EventEntry':
            return EventEntry(**data)
        elif entry_type_name == 'HabitEntry':
            return HabitEntry(**data)
        elif entry_type_name == 'NoteEntry':
            return NoteEntry(**data)
        else:
            # Fallback for unknown/old types
            return JournalEntry(type=entry_type_name, **data)


# ============================================================================
# CUSTOM JSON ENCODER
# ============================================================================

class CustomEncoder(json.JSONEncoder):
    """
    Custom JSON Encoder to handle non-standard types (datetime, Enum, dataclass)
    for proper serialization.
    """
    
    def default(self, o: Any) -> Any:
        # Handle dataclass objects by converting to a dictionary
        if isinstance(o, JournalEntry):
            data = o.__dict__.copy()
            data["_type"] = o.__class__.__name__
            return data

        # Handle datetime objects
        if isinstance(o, datetime):
            return o.isoformat()

        # Handle Enum objects
        if isinstance(o, Enum):
            return o.value
        
        # Let the base class handle all other types
        return super().default(o)


# ============================================================================
# MODULE-LEVEL FUNCTIONS (Backward Compatibility)
# ============================================================================

# Create a default repository instance
_default_repository = FileJournalRepository()

def load_entries() -> List[JournalEntry]:
    """Loads journal entries using the default file repository."""
    return _default_repository.load_entries()

def save_entries(entries: List[JournalEntry]) -> None:
    """Saves journal entries using the default file repository."""
    _default_repository.save_entries(entries)
