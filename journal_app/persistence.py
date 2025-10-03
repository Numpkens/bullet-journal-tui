import json
from datetime import datetime
from enum import Enum
from journal_app.entry import Signifier 

class CustomEncoder(json.JSONEncoder):
    """
    Custom JSON Encoder to handle non-standard types (datetime, Enum)
    for proper serialization.
    """
    def default(self, obj):
        # 1. Handle datetime objects by converting to ISO 8601 string
        if isinstance(obj, datetime):
            return obj.isoformat()

        # 2. Handle Enum objects by converting to their underlying value
        if isinstance(obj, Enum):
            return obj.value
        
        # 3. Fallback for all other types
        return super().default(obj)
