# Bullet Journal TUI

## Description
This project is a Python-based Text User Interface (TUI) application designed for structured data management, functioning as a digital bullet journal. The primary goal is to establish a clear separation of concerns between the application's business logic (data modeling) and the presentation layer (the TUI). It demonstrates proficiency in managing application state, implementing robust input validation, and designing scalable data persistence mechanisms (using Python's file I/O, with future plans for SQLite/PostgreSQL integration). This modular architecture is directly transferable to building and securing production-grade REST APIs.

## Rationale & Architectural Design
The architecture prioritizes the core backend challenges required for a Go developer:

    - State Management: The application's complex state (tasks, entries, dates) is managed internally, requiring explicit logic to handle state transitions—a key skill for managing concurrent requests in a distributed system.

    - Persistence Layer Design: The design treats the file system/database as an external service. This separation ensures the entire business logic layer could be swapped into a different presentation environment (e.g., a web framework or a Go API) without modifying the core data models.

    TUI as a High-Fidelity Interface: Using the Textual TUI library forces complex event handling and input validation logic, simulating the difficulty of maintaining high data integrity across a user interface—a critical requirement for high-stakes backend systems.

    Future Iteration: The next planned step is to integrate a dedicated database (SQLite/PostgreSQL) and implement basic CRUD operations on the data models to further solidify database proficiency.

## Getting Started


## Usage


## File Structure


## Contributing

Contributions are welcome! If you find a bug or have an idea for a new feature, please open an issue or submit a pull request.

✍️ Author

David Gagnon - Numpkens

## Daily Log

**10/2/2025** Today, I am planning the structure and using the README and a draft for the inital plan. 
    **-Project Setup:**	Finalized folder structure, app.py, and tests/tests_app.py.	Established separation of concerns between the application logic (journal_app) and testing infrastructure (tests).
    **-Dependencies	Installed:** textual and pytest using the Zsh-safe command: pip install pytest 'textual[dev]'.	Overcame a common shell-specific environment issue (Zsh globbing) to ensure a robust testing setup.
    **-Environment**	Created and activated a dedicated virtual environment (venv).	Ensured project isolation and dependency reproducibility, a critical practice for production-grade code.
    **-Version Control**	Created a comprehensive .gitignore file.	Maintained a clean Git history by excluding environment files (venv/), caches, and future persistence files (*.db).

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
