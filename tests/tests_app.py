from textual.app import App
from textual.app_test import AppTest
from journal_app.app import BulletJournalApp
from journal_app.entry import TaskEntry, Signifier, EventEntry, NoteEntry, HabitEntry
from datetime import datetime
from dataclasses import dataclass, field


async def test_app_starts_and_has_widgets():
    """Test that the app composes the essential widgets (Header, Footer, Container)."""
    app_test = AppTest(BulletJournalApp)

    await app_test.compose()

    # Assertions: Check if the key widgets are present in the DOM (Document Object Model)
    assert app_test.app.query_one("Header")
    assert app_test.app.query_one("Footer")
    assert app_test.app.query_one("#app-grid") # Check for the main container by its ID
    assert app_test.app.query_one("#welcome-message") # Check for the welcome label


def test_task_entry_defaults():
    task = TaskEntry(content="Call the doctor")
    assert task.type == "Task"
    assert task.status == "Pending"
    assert task.signifier == Signifier.NONE
    assert task.content == "Call the doctor"


def test_event_entry_defaults():
    event = EventEntry(content="Doctor Appointment")
    assert event.type == "Event"
    assert event.location is None
    assert isinstance(event.timestamp, datetime)


def test_note_entry_defaults():
    note = NoteEntry(content="Idea for a new feature")
    assert note.type == "Note"
    assert note.signifier == Signifier.NONE
    assert isinstance(note.timestamp, datetime)


def test_habit_entry_defaults():
    habit = HabitEntry(content="Read for 30 minutes")
    assert habit.type == "Habit"
    assert habit.frequency == "Daily"
    assert habit.progress == [] 
    assert habit.progress is not []
