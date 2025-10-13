# CLI Bullet Journal - Ryder Carroll Method

## Description
A Python-based **Command Line Interface (CLI)** application implementing the core concepts of the Ryder Carroll Bullet Journal methodology. This application is structured as a Python package (`journal_app/`) and uses file-based (JSON) persistence for a simple, functional digital journaling experience.

## Core Features
* **Rapid Logging:** Add Notes (`−`), Incomplete Tasks (`•`), Events (`○`), and Habits.
* **Task Workflows:** Mark tasks as Completed (`×`) or Migrated (`>`).
* **Spreads:** Dedicated, tabular views for **Weekly Spread**, **Monthly Spread**, and a **Habit Tracker**.
* **Persistence:** All entries are automatically saved to `journal_data.json` upon exit.
* **Instructional Placeholders:** Starts with simple entries that guide the new user through commands.

## Setup and Installation

### Prerequisites
* Python 3.x

### Installation Steps

1.  **Navigate** to the project root directory (`bullet-journal-tui`).
2.  **Install** the required Python packages (primarily `tabulate` for table rendering):

    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

Since the application uses a package structure, execute the main file using the module execution flag (`-m`) from the root directory:

```bash
python -m journal_app.app
```
 ### CLI Usage

The main loop displays current entries and presents a menu with single-letter commands for rapid logging and management:
Command	Action	Description
A	Add Entry	Create a new Note, Task, Event, or Habit.
X	Complete Task	Marks an incomplete task (•) as completed (×).
M	Migrate Task	Marks an incomplete task (•) as migrated (>).
H	Complete Habit	Logs a habit as completed (+) for the current day.
C	Complete Event	Marks an event as complete (✓).
V	View Spreads	Opens a sub-menu to view Habit, Weekly, or Monthly spreads.
Q	Quit & Save	Saves all current entries to the journal_data.json file and exits the program.
