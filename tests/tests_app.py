import pytest
import os
from pathlib import Path

# Import the main app and persistence functions
from journal_app.app import BulletJournalApp
from journal_app.entry import NoteEntry, TaskEntry, Signifier
from journal_app.persistence import DATA_FILE, load_entries, save_entries

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
    
    # Note: We don't restore os.chdir because Textual's tester handles the app context.

# --- Persistence Tests ---

def test_save_load_empty_entries(temp_data_file):
    """Test saving and loading an empty list of entries."""
    entries = []
    save_entries(entries)
    
    loaded = load_entries()
    assert loaded == []
    assert os.path.exists(DATA_FILE)

def test_load_non_existent_file():
    """Test loading when the data file does not exist."""
    # Ensure the file is not there
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        
    loaded = load_entries()
    assert loaded == []

def test_save_load_mixed_entries(temp_data_file):
    """Test saving and loading a mix of different entry types."""
    # 1. Setup various entries
    task = TaskEntry(content="Buy milk", signifier=Signifier.PRIORITY)
    note = NoteEntry(content="Meeting notes", type="Note")
    
    # The timestamp will be converted to an ISO string and back, 
    # so we must compare the saved/loaded objects, not the references.
    entries_to_save = [task, note]
    
    # 2. Save
    save_entries(entries_to_save)
    
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
async def test_app_starts_and_shows_journal_screen(temp_data_file):
    """Test that the app starts and mounts the JournalScreen."""
    app = BulletJournalApp()
    
    async with app.run_test() as harness:
        # Check if the JournalScreen is mounted
        assert harness.app.screen.id == "journal"
        
        # Check the initial number of entries (it should add the 'Welcome' note)
        assert len(app.entries) == 1
        
        # Check the welcome message content (from the initial NoteEntry)
        welcome_entry_content = harness.app.query_one(".note").entry.content
        assert "Welcome" in welcome_entry_content
        
@pytest.mark.asyncio
async def test_app_quits_and_saves_data(temp_data_file, monkeypatch):
    """Test that the application saves its current state when quitting."""
    # We will track if the save_entries function is called
    save_called = False

    def mock_save_entries(entries):
        nonlocal save_called
        save_called = True
        # Call the real save logic to create a file for a subsequent load test
        save_entries(entries) 

    # Use monkeypatch to replace the real save_entries with our mock
    monkeypatch.setattr("journal_app.app.save_entries", mock_save_entries)

    # 1. Run the app
    app = BulletJournalApp()
    async with app.run_test() as harness:
        # Add a test entry to the app's state
        test_entry = NoteEntry("Test entry before quit", type="Note")
        app.entries.append(test_entry)
        
        # 2. Perform the quit action
        await harness.app.action_quit()
        
    # 3. Assertions after the app has closed
    assert save_called is True

    # 4. Verify the saved data actually contains the new entry
    loaded_entries = load_entries()
    assert len(loaded_entries) == 2 # 1 initial + 1 test entry
    assert loaded_entries[-1].content == "Test entry before quit"
