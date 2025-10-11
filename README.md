# Bullet Journal TUI - Project: Enterprise Persistence Contract (Python)

## Description
This project is a Python-based Text User Interface (TUI) serving as an **Architectural Proof-of-Concept** for structured data management. It demonstrates proficiency in **Enterprise Patterns** by implementing a **Decoupling Strategy** for data persistence. The design uses Python's file I/O, with the architecture directly prepared for quick swapping to **SQL Server** or PostgreSQL.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                      │
│  ┌─────────────────┐         ┌──────────────────┐          │
│  │  JournalScreen  │         │ NewEntryScreen   │          │
│  │  (Textual UI)   │         │  (Textual UI)    │          │
│  └────────┬────────┘         └────────┬─────────┘          │
│           │                           │                     │
└───────────┼───────────────────────────┼─────────────────────┘
            │                           │
            ▼                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
│                  (BulletJournalApp)                         │
│                                                             │
│     entries: List[JournalEntry]                            │
│     ├── TaskEntry                                          │
│     ├── NoteEntry                                          │
│     ├── EventEntry                                         │
│     └── HabitEntry                                         │
│                                                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Uses (Dependency Injection)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Persistence Contract (Protocol)                │
│                                                             │
│            ┌─────────────────────────────┐                 │
│            │  JournalRepository          │                 │
│            │  ├─ load_entries()          │                 │
│            │  ├─ save_entries()          │                 │
│            │  └─ find_by_date_range()    │                 │
│            └──────────────┬──────────────┘                 │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            │ Implemented by
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│ FileJournalRepository    │  │ SQLServerRepository      │
│                          │  │                          │
│ - JSON file storage      │  │ - SQL Server database    │
│ - CustomEncoder/Decoder  │  │ - CRUD operations        │
│ - Error handling         │  │ - Transaction support    │
│ - Logging                │  │ - Relational model       │
└──────────────────────────┘  └──────────────────────────┘
```

## Rationale & Architectural Design

The architecture prioritizes the core backend challenges required for a Go developer:

- **State Management**: The application's complex state (tasks, entries, dates) is managed internally, requiring explicit logic to handle state transitions—a key skill for managing concurrent requests in a distributed system.

- **Persistence Contract (Interface Design)**: The core business logic interacts exclusively with a `JournalRepository` **interface** (using Python `typing.Protocol`). This treats the storage (file system/database) as an external service, achieving complete **architectural decoupling**. The logic is fully independent of the underlying storage technology (file I/O, **SQL Server**, etc.).

- **Clean Architecture Demonstration**: Using the TUI library forces complex event handling and input validation logic, simulating the need for maintaining **high data integrity** and **security** at the application boundary.

- **Production-Ready Patterns**: Implements logging, error handling, and transaction-like semantics to demonstrate enterprise-grade code quality.

## Features

✅ **Implemented**
- Rapid logging interface (Notes, Tasks, Events, Habits)
- Signifier support (Priority *, Inspiration #)
- Task completion and migration workflows
- Future Log filtering by year/month
- File-based persistence with JSON
- Repository pattern with Protocol interface
- SQL Server repository implementation (ready to use)
- Comprehensive test suite
- Rose Pine Moon color theme

🚧 **In Progress**
- Daily/Monthly log dedicated views
- Habit tracker progress UI

## Getting Started

### Prerequisites
```bash
# Python 3.10 or higher
python --version

# Create virtual environment
python -m venv venv

# Activate environment
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For SQL Server support (optional):
pip install pyodbc
```

### Running the Application

```bash
# Run with file-based storage (default)
python -m journal_app.app

# Or directly
python journal_app/app.py
```

### Using SQL Server (Optional)

1. Create a SQL Server database:
```sql
CREATE DATABASE BulletJournal;
```

2. Run the schema from `journal_app/sql_repository.py`

3. Modify `app.py` to use SQL Server:
```python
from journal_app.sql_repository import SQLServerRepository

def __init__(self, **kwargs):
    super().__init__(**kwargs)
    
    # Use SQL Server instead of file storage
    self.repository = SQLServerRepository(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=BulletJournal;"
        "UID=your_user;"
        "PWD=your_password"
    )
    self.entries = self.repository.load_entries()
```

## Usage

### Keyboard Shortcuts
- `n` - Create new entry
- `q` - Quit and save
- `x` - Complete selected task
- `m` - Migrate selected task
- `f` - Toggle Future Log filter
- `Esc` - Go back / Close dialog

### Creating Entries
1. Press `n` to open the New Entry screen
2. Select entry type (Note, Task, Event)
3. Choose signifier (Priority, Inspiration, or None)
4. Enter your content
5. Press "Add Entry"

### Filtering Entries
1. Press `f` to show filter controls
2. Select year and/or month
3. Click "Apply Filter"
4. Press `f` again to clear filter

## File Structure

```
bullet-journal-tui/
├── journal_app/
│   ├── __init__.py
│   ├── app.py              # Main application
│   ├── app.css             # Rose Pine Moon theme
│   ├── entry.py            # Data models
│   ├── persistence.py      # Repository interface & file implementation
│   ├── sql_repository.py   # SQL Server implementation
│   └── screens.py          # UI screens
├── tests/
│   ├── __init__.py
│   └── tests_app.py        # Comprehensive test suite
├── journal_data.json       # Data file (created on first run)
├── requirements.txt
├── README.md
└── .gitignore
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=journal_app

# Run specific test file
pytest tests/tests_app.py

# Run with verbose output
pytest -v
```

## Key Design Patterns

### 1. Repository Pattern
Decouples data access from business logic through a Protocol interface:
```python
class JournalRepository(Protocol):
    def load_entries(self) -> List[JournalEntry]: ...
    def save_entries(self, entries: List[JournalEntry]) -> None: ...
```

### 2. Dependency Injection
The app can work with any repository implementation:
```python
class BulletJournalApp(App):
    def __init__(self, repository=None, **kwargs):
        self.repository = repository or FileJournalRepository()
```

### 3. Data Transfer Objects
Immutable dataclasses ensure type safety:
```python
@dataclass
class TaskEntry(JournalEntry):
    type: str = "Task"
    status: str = "Pending"
```

### 4. Custom Serialization
Handles complex types (datetime, Enum) transparently:
```python
class CustomEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()
```

## Contributing

Contributions are welcome! If you find a bug or have an idea for a new feature, please open an issue or submit a pull request.

### Development Setup
```bash
# Install dev dependencies
pip install pytest pytest-cov textual[dev]

# Run tests before committing
pytest

# Format code (optional)
black journal_app/
```

## Daily Log

**10/2/2025** - Project initialization and setup
- Finalized folder structure, app.py, and tests/tests_app.py
- Established separation of concerns between application logic and testing infrastructure
- Installed textual and pytest
- Created virtual environment (venv)
- Created comprehensive .gitignore file

**10/3/2025** - Established Enterprise Patterns
- Defined the `JournalRepository` **Interface** (using `typing.Protocol`)
- Implemented the concrete `FileJournalRepository`
- Used `@dataclass` and inheritance for type-safe data models
- Demonstrated architectural decoupling for database integration

**10/11/2025** - Major refinements and SQL implementation
- Fixed dummy data override bug (now only loads on empty journal)
- Corrected CSS property issues (`text` → `text-style`)
- Fixed test suite issues with proper mocking and assertions
- Enhanced persistence.py with logging and error handling
- Implemented full `SQLServerRepository` with CRUD operations
- Added comprehensive test coverage for new features
- Updated documentation with architecture diagram

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

---

**Author**: David Gagnon - Numpkens


🔗 **Portfolio**: Demonstrates understanding of:
- Clean Architecture
- SOLID Principles
- Repository Pattern
- Dependency Injection
- Type Safety
- Error Handling
- Testing Strategies
- Database Design
