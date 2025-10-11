import json
import os
from datetime import datetime
from enum import Enum
# Import necessary types and dataclass inspection functions
from typing import List, Union, Any 
from dataclasses import fields as dataclass_fields

# Import all entry classes and Signifier from the entry module
from journal_app.entry import (
    Signifier,
    JournalEntry,
    TaskEntry,
    EventEntry,
    NoteEntry,
    HabitEntry
)

# Define the data file path
DATA_FILE = "journal_data.json"

class CustomEncoder(json.JSONEncoder):
    """
    Custom JSON Encoder to handle non-standard types (datetime, Enum, dataclass)
    for proper serialization.
    """
    # Parameter 'o' matches the base class signature (linter fix).
    def default(self, o: Any) -> Any:
        # 1. Handle dataclass objects by converting to a dictionary
        if isinstance(o, JournalEntry):
            data = o.__dict__.copy()
            data["_type"] = o.__class__.__name__
            return data

        # 2. Handle datetime objects
        if isinstance(o, datetime):
            return o.isoformat()

        # 3. Handle Enum objects
        if isinstance(o, Enum):
            return o.value
        
        # 4. Let the base class handle all other types
        return super().default(o)

def decode_entry(data: dict) -> Union[JournalEntry, dict]:
    """
    Decodes a dictionary back into the correct JournalEntry dataclass.
    """
    # Mapping of class names to their actual classes
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
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])

        # Convert signifier value back to Signifier Enum
        if "signifier" in data and isinstance(data["signifier"], str):
            data["signifier"] = Signifier(data["signifier"])


        # Instantiate the correct dataclass
        if entry_type in class_map:
            entry_class = class_map[entry_type]
            
            # FIX: Use dataclass_fields for safe instantiation (prevents runtime AttributeError)
            # 1. Get the list of valid field names for the dataclass
            valid_keys = {f.name for f in dataclass_fields(entry_class)}
            
            # 2. Filter the incoming data to only include valid keys
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}
            
            try:
                # 3. Instantiate the dataclass with the filtered data
                return entry_class(**filtered_data)
            except TypeError as e:
                # Fallback for old/corrupted data
                print(f"Error creating entry of type {entry_type}: {e}")
                return data

    return data

def load_entries() -> List[JournalEntry]:
    """Loads journal entries from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    
    with open(DATA_FILE, "r") as f:
        try:
            # Handle empty file case
            content = f.read()
            if not content:
                return []
            
            data = json.loads(content, object_hook=decode_entry)
            return [e for e in data if isinstance(e, JournalEntry)]
        except json.JSONDecodeError:
            print("Error decoding JSON data. Starting with an empty journal.")
            return []

def save_entries(entries: List[JournalEntry]):
    """Saves journal entries to the JSON file."""
    with open(DATA_FILE, "w") as f:
        # Use the custom encoder to handle dataclasses, datetime, and enums
        json.dump(entries, f, indent=4, cls=CustomEncoder)
