Develop a Python web application named "Flashcard", designed to run locally on user machines via Docker or Podman. Use the Flask framework and SQLite3 for the database.

**Core Requirements:**

1.  **Containerization:** Package the application in a Docker container. Provide a `Dockerfile` using a Python base image (e.g., `python:3.10-slim`), a `requirements.txt` file (including Flask), and instructions for building and running the container, ensuring data persistence via volume mounting for the database and user progress. The application should be accessible via a mapped port (e.g., 5000).
2.  **Database (`flashcard.db`):**
    *   Use SQLite3, stored within the persistent volume (`/data/flashcard.db`).
    *   Schema:
        *   `datasets` table: `id` (INTEGER PRIMARY KEY AUTOINCREMENT), `name` (TEXT UNIQUE NOT NULL).
        *   `cards` table: `id` (INTEGER PRIMARY KEY AUTOINCREMENT), `dataset_id` (INTEGER, FOREIGN KEY (`dataset_id`) REFERENCES `datasets` (`id`)), `question` (TEXT NOT NULL), `correct_answer` (TEXT NOT NULL), `choice1` (TEXT NOT NULL), `choice2` (TEXT NOT NULL), `choice3` (TEXT NOT NULL), `choice4` (TEXT NOT NULL), `choice5` (TEXT).
    *   Initialization: Automatically create the database and tables if they don't exist on application startup.
3.  **Data Import:**
    *   Implement a web page allowing users to upload a CSV file and provide a unique name for the dataset.
    *   CSV Structure: 7 columns in order: `question`, `correct_answer`, `answer_choice_1`, `answer_choice_2`, `answer_choice_3`, `answer_choice_4`, `answer_choice_5` (column 7 is optional and can be empty). Assume no header row for parsing simplicity, or handle optional header.
    *   Validation: Prevent duplicate dataset names. Handle potential CSV parsing errors gracefully.
    *   Processing: Upon successful upload, create a new entry in the `datasets` table and populate the `cards` table with the data from the CSV, linking cards to the dataset via `dataset_id`.
4.  **User Interface & Workflow:**
    *   **Dataset Selection Page:** The main entry point. Display a list of all available dataset names from the `datasets` table. Clicking a dataset name navigates to the Flashcard Learning Page for that dataset.
    *   **Flashcard Learning Page:**
        *   Displays one card at a time from the selected dataset.
        *   Initially shows the `question` text and all associated answer `choices` (4 or 5).
        *   Implement an interactive element (e.g., clicking the card area) to reveal the `correct_answer` for the current card.
        *   Provide "Next" and "Previous" buttons to navigate sequentially through all cards within the selected dataset.
        *   Include a "Back to Datasets" button/link to return to the Dataset Selection Page.
5.  **Progress Persistence:**
    *   For each dataset, track the index (or ID) of the last viewed card.
    *   Store this progress persistently (e.g., in a simple key-value file like `progress.json` within the persistent volume `/data/`). The structure could be `{ "dataset_id": last_card_index }`.
    *   When a user selects a dataset from the Dataset Selection Page, load its progress and display the corresponding card. If no progress is saved for that dataset, start from the first card (index 0). Update the progress file whenever the user navigates to a new card.
6.  **Code Structure & Maintainability:** Organize the code logically (e.g., `app.py`, `database.py`, `templates/`, `static/`). Use clear, maintainable code with comments where necessary. Ensure robust error handling for file operations, database interactions, and user input.