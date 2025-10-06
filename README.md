# Bullet Journal TUI - Project: Enterprise Persistence Contract (Python)

## Description
This project is a Python-based Text User Interface (TUI) serving as an **Architectural Proof-of-Concept** for structured data management. It demonstrates proficiency in **Enterprise Patterns** by implementing a **Decoupling Strategy** for data persistence. The design uses Python's file I/O, with the architecture directly prepared for quick swapping to **SQL Server** or PostgreSQL

## Rationale & Architectural Design
The architecture prioritizes the core backend challenges required for a Go developer:

    - State Management: The application's complex state (tasks, entries, dates) is managed internally, requiring explicit logic to handle state transitions—a key skill for managing concurrent requests in a distributed system.
    - **Persistence Contract (Interface Design):** The core business logic interacts exclusively with a JournalRepository**interface** (using Pythontyping.Protocol). This treats the storage (file system/database) as an external service, achieving complete **architectural decoupling**. The logic is fully independent of the underlying storage technology (file I/O, **SQL Server**, etc.)

    - **Clean Architecture Demonstration:** Using the TUI library forces complex event handling and input validation logic, simulating the need for maintaining **high data integrity** and **security** at the application boundary.

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

**10/3/2025** Established **Enterprise Patterns** for architectural robustness.<br>**- Persistence Contract:** Defined the JournalRepository**Interface** (usingtyping.Protocol) to decouple the application logic from the persistence layer. This design allows for immediate integration with **SQL Server** or other relational databases, a key practice for enterprise applications.<br>**- Decoupling:** Implemented the concrete FileJournalRepositorywhich adheres to the interface, proving the system's modularity and testability.<br>**- Data Models:** Used@dataclass and inheritance to create a rigid, type-safe data model (a prerequisite for **Clean Code** in distributed systems).

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
