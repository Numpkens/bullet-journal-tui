import json
import os
import logging
from datetime import datetime
from enum import Enum
from typing import List, Union, Any, Protocol
from dataclasses import fields as dataclass_fields

from journal_app.entry import (
    Signifier,
    JournalEntry,
    TaskEntry,
    EventEntry,
    NoteEntry,
    HabitEntry
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the data file path
DATA_FILE = "journal_data.json"


# ============================================================================
# REPOSITORY PATTERN - Interface Definition (Enterprise Design)
# ============================================================================

class JournalRepository(Protocol):
    """
    Repository interface for journal data persistence.
    This protocol defines the contract that any persistence implementation must follow.
    Enables easy swapping between file-based, SQL Server, PostgreSQL, etc.
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

class FileJournalRepository:
    """
    File-based implementation of the JournalRepository interface.
    Uses JSON for serialization with custom encoding/decoding.
    """
    
    def __init__(self, file_path: str = DATA_FILE):
        self.file_path = file_path
    
    def load_entries(self) -> List[JournalEntry]:
        """Loads journal entries from the JSON file."""
        if not os.path.exists(self.file_path):
            logger.info(f"Data file not found: {self.file_path}. Starting with empty journal.")
            return []
        
        try:
            with open(self.file_path, "r") as f:
                content = f.read()
                if not content:
                    logger.warning(f"Data file is empty: {self.file_path}")
                    return []
                
                data = json.loads(content, object_hook=self._decode_entry)
                entries = [e for e in data if isinstance(e, JournalEntry)]
                logger.info(f"Successfully loaded {len(entries)} entries from {self.file_path}")
                return entries
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {self.file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error loading entries: {e}")
            return []
    
    def save_entries(self, entries: List[JournalEntry]) -> None:
        """Saves journal entries to the JSON file."""
        try:
            with open(self.file_path, "w") as f:
                json.dump(entries, f, indent=4, cls=CustomEncoder)
            logger.info(f"Successfully saved {len(entries)} entries to {self.file_path}")
            
        except Exception as e:
            logger.error(f"Error saving entries: {e}")
            raise
    
    def find_by_date_range(self, start: datetime, end: datetime) -> List[JournalEntry]:
        """Find entries within a specific date range."""
        entries = self.load_entries()
        return [
            e for e in entries 
            if start <= e.timestamp <= end
        ]
    
    def _decode_entry(self, data: dict) -> Union[JournalEntry, dict]:
        """
        Decodes a dictionary back into the correct JournalEntry dataclass.
        """
        class_map = {
            "TaskEntry": TaskEntry,
            "EventEntry": EventEntry,
            "NoteEntry": NoteEntry,
            "HabitEntry": HabitEntry,
            "JournalEntry": JournalEntry,
        }

        if "_type" in data:
            entry_type = data.pop("_type")
            
            # Convert timestamp string back to datetime object
            if "timestamp" in data and isinstance(data["timestamp"], str):
                try:
                    data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                except ValueError as e:
                    logger.warning(f"Invalid timestamp format: {e}")
                    data["timestamp"] = datetime.now()

            # Convert signifier value back to Signifier Enum
            if "signifier" in data and isinstance(data["signifier"], str):
                try:
                    data["signifier"] = Signifier(data["signifier"])
                except ValueError:
                    data["signifier"] = Signifier.NONE

            # Instantiate the correct dataclass
            if entry_type in class_map:
                entry_class = class_map[entry_type]
                
                # Get valid field names for the dataclass
                valid_keys = {f.name for f in dataclass_fields(entry_class)}
                
                # Filter data to only include valid keys
                filtered_data = {k: v for k, v in data.items() if k in valid_keys}
                
                try:
                    return entry_class(**filtered_data)
                except TypeError as e:
                    logger.error(f"Error creating entry of type {entry_type}: {e}")
                    return data

        return data


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
