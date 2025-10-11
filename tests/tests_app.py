import pytest
import os
from pathlib import Path

# Import the main app and persistence functions
from journal_app.app import BulletJournalApp
from journal_app.entry import NoteEntry, TaskEntry, Signifier
from journal_app.persistence import DATA_FILE, load_entries, save_entries as real_save_entries

# --- Fixtures for Testing ---

@pytest.fixture
def temp_data_file(tmp_path: Path):
    """
    Fixture to create a temporary DATA_FILE path for testing.
    This ensures tests don't interfere with real data.
    """
    # Temporarily change the working directory to the pytest temp directory
    # so DATA_FILE is created there.
    os.chdir(tmp_path) 
    
    yield tmp_path / DATA_FILE
    
    # Clean up: Remove the data file after the test if it exists
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

# --- Persistence Tests ---

def test_save_load_empty_entries(temp_data_file: Path):
    """Test saving and loading an empty list of entries."""
    _ = temp_data_file  # Acknowledge fixture usage
    entries = []
    real_save_entries(entries)
    
    loaded = load_entries()
    assert loaded == []
    assert os.path.exists(DATA_FILE)

def test_load_non_existent_file(temp_data_file: Path):
    """Test loading when the data file does not exist."""
    _ = temp_data_file  # Acknowledge fixture usage
    # Ensure the file is not there
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        
    loaded = load_entries()
    assert loaded == []

def test_save_load_mixed_entries(temp_data_file: Path):
    """Test saving and loading a mix of different entry types."""
    _ = temp_data_file  # Acknowledge fixture usage
    # 1. Setup various entries
    task = TaskEntry(content="Buy milk", signifier=Signifier.PRIORITY)
    note = NoteEntry(content="Meeting notes", type="Note")
    
    # The timestamp will be converted to an ISO string and back, 
    # so we must compare the saved/loaded objects, not the references.
    entries_to_save = [task, note]
    
    # 2. Save
    real_save_entries(entries_to_save)
    
    # 3. Load
    loaded_entries = load_entries()
    
    # 4. Assertions
    assert len(loaded_entries) == 2
    
    # Check the loaded TaskEntry
    loaded_task = loaded_entries[0]
    assert isinstance(loaded_task, TaskEntry)
    assert loaded_task.content == "Buy milk"
    assert loaded_task.signifier == Signifier.PRIORITY
    assert loaded_task.status == "Pending" # Default status
    
    # Check the loaded NoteEntry
    loaded_note = loaded_entries[1]
    assert isinstance(loaded_note, NoteEntry)
    assert loaded_note.content == "Meeting notes"
    assert loaded_note.type == "Note"

# --- Application Tests ---

@pytest.mark.asyncio
async def test_app_starts_and_shows_journal_screen(temp_data_file: Path):
    """Test that the app starts and mounts the JournalScreen."""
    _ = temp_data_file  # Acknowledge fixture usage
    app = BulletJournalApp()
    
    async with app.run_test():
        # Check if the JournalScreen is mounted
        assert app.screen.id == "journal"
        
        # Check entries directly from app state
        assert len(app.entries) >= 1
        
        # Check the welcome message content (from the first entry)
        assert "Welcome" in app.entries[0].content
        
@pytest.mark.asyncio
async def test_app_quits_and_saves_data(temp_data_file: Path, monkeypatch):
    """Test that the application saves its current state when quitting."""
    _ = temp_data_file  # Acknowledge fixture usage
    # We will track if the save_entries function is called
    save_called = False

    def mock_save_entries(entries):
        nonlocal save_called
        save_called = True
        # Call the real save logic using the imported name
        real_save_entries(entries) 

    # Use monkeypatch to replace the real save_entries with our mock
    monkeypatch.setattr("journal_app.app.save_entries", mock_save_entries)

    # 1. Run the app
    app = BulletJournalApp()
    async with app.run_test():
        # Add a test entry to the app's state
        test_entry = NoteEntry("Test entry before quit", type="Note")
        app.entries.append(test_entry)
        
        # 2. Perform the quit action
        await app.action_quit()
        
    # 3. Assertions after the app has closed
    assert save_called is True

    # 4. Verify the saved data actually contains the new entry
    loaded_entries = load_entries()
    # The app starts with 3 dummy entries (if empty) + 1 test entry = 4 total
    assert len(loaded_entries) >= 2
    assert any("Test entry before quit" in entry.content for entry in loaded_entries)


# --- New Tests for Enhanced Coverage ---

@pytest.mark.asyncio
async def test_new_entry_screen_navigation(temp_data_file: Path):
    """Test that pressing 'n' navigates to the New Entry screen."""
    _ = temp_data_file  # Acknowledge fixture usage
    app = BulletJournalApp()
    
    async with app.run_test() as pilot:
        # Press 'n' to navigate to new entry screen
        await pilot.press("n")
        await pilot.pause()
        
        # Check that we're now on the NewEntryScreen
        # The screen stack should have 2 screens now
        assert len(app.screen_stack) == 2

@pytest.mark.asyncio  
async def test_task_completion(temp_data_file: Path):
    """Test completing a task with the 'x' key."""
    _ = temp_data_file  # Acknowledge fixture usage
    app = BulletJournalApp()
    
    async with app.run_test() as pilot:
        # Ensure we have at least one task
        task = TaskEntry("Test task", status="Pending")
        app.entries.append(task)
        
        # Update the list view
        from journal_app.screens import JournalScreen
        journal_screen = app.query_one("#journal", JournalScreen)
        journal_screen.update_list()
        await pilot.pause()
        
        # Select the task and complete it
        await pilot.press("x")
        await pilot.pause()
        
        # Check that the task status changed - narrow the type first
        test_task = next((e for e in app.entries if e.content == "Test task"), None)
        assert test_task is not None
        assert isinstance(test_task, TaskEntry)  # Type narrowing
        assert test_task.status == "Complete"

@pytest.mark.asyncio
async def test_filter_visibility_toggle(temp_data_file: Path):
    """Test toggling the filter view with 'f' key."""
    _ = temp_data_file  # Acknowledge fixture usage
    app = BulletJournalApp()
    
    async with app.run_test() as pilot:
        # Get the filter container
        from textual.containers import Container
        filter_container = app.query_one("#future-log-filters", Container)
        initial_visibility = filter_container.display
        
        # Press 'f' to toggle
        await pilot.press("f")
        await pilot.pause()
        
        # Check that display property changed
        assert filter_container.display != initial_visibility
