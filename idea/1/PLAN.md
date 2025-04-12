# Flashcard Application Development Plan

This document outlines the plan for developing the "Flashcard" Python web application using Flask and SQLite, containerized with Docker/Podman.

## Confirmed Specifications

*   **CSV Import:** Assume no header row.
*   **Styling:** Implement using basic, custom CSS.
*   **Error Handling:** Display errors using Flask's flash messaging system.
*   **Card Navigation:** No wrap-around (Next/Previous disabled at ends).
*   **Answer Reveal:** Clicking the card area reveals the answer.

## Phase 1: Project Setup & Core Backend

1.  **Define Project Structure:**
    *   Create the main project directory: `flashcard_app/`
    *   Inside `flashcard_app/`, create:
        *   `app.py`: Main Flask application file.
        *   `database.py`: Module for database interactions.
        *   `requirements.txt`: Python dependencies.
        *   `Dockerfile`: Container build instructions.
        *   `templates/`: Directory for HTML templates.
        *   `static/`: Directory for CSS/JS files.
    *   A separate `data/` directory will be used as a volume mount point for persistent storage (`/data/flashcard.db`, `/data/progress.json`).

2.  **Containerization (`Dockerfile`, `requirements.txt`):**
    *   `requirements.txt`: List `Flask`.
    *   `Dockerfile`:
        *   Base image: `python:3.10-slim`.
        *   Working directory: `/app`.
        *   Install dependencies from `requirements.txt`.
        *   Copy application code.
        *   Define volume mount point: `/data`.
        *   Expose port: 5000.
        *   Run command: `flask run --host=0.0.0.0`.

3.  **Database Module (`database.py`):**
    *   Functions:
        *   `init_db()`: Connect to `/data/flashcard.db`, create tables (`datasets`, `cards`) if they don't exist.
        *   `add_dataset(name)`: Add dataset, handle unique name constraint.
        *   `add_card(...)`: Add card linked to a dataset.
        *   `get_datasets()`: Return list of all datasets.
        *   `get_cards_by_dataset(dataset_id)`: Return all cards for a dataset (ordered).
        *   `get_dataset_id_by_name(name)`: Check if dataset name exists.

## Phase 2: Flask Application Logic (`app.py`)

1.  **Initialization:**
    *   Create Flask app instance.
    *   Call `database.init_db()` on startup.
    *   Define progress file path: `/data/progress.json`.
    *   Implement helper functions `load_progress()` and `save_progress(dataset_id, card_index)`. Handle file/JSON errors.

2.  **Routes & Views:**
    *   **`/` (GET): Dataset Selection & Upload**
        *   Fetch datasets via `database.get_datasets()`.
        *   Render `index.html` (pass datasets).
    *   **`/upload` (POST): Data Import**
        *   Get `dataset_name` and `csv_file`.
        *   Validate name (non-empty, unique).
        *   Parse CSV (no header assumed). Handle errors.
        *   Insert data into DB (`add_dataset`, `add_card`). Use transaction.
        *   Redirect to `/` with flash message (success/error).
    *   **`/learn/<int:dataset_id>` (GET): Flashcard Learning (Entry)**
        *   Load progress for `dataset_id`. Default to index 0.
        *   Redirect to `/learn/<int:dataset_id>/<int:card_index>`.
    *   **`/learn/<int:dataset_id>/<int:card_index>` (GET): Display Specific Card**
        *   Fetch cards via `database.get_cards_by_dataset()`.
        *   Validate `card_index`.
        *   Get specific card data.
        *   Save progress using `save_progress()`.
        *   Render `learn.html` (pass card data, index, total, dataset ID).

## Phase 3: Frontend (`templates/`, `static/`)

1.  **Templates (`templates/`):**
    *   `base.html` (Optional): Common structure.
    *   `index.html`: Flash messages, upload form, dataset list (links to `/learn/<id>`).
    *   `learn.html`: Card count, question, choices, hidden answer (reveal on click), Prev/Next buttons (disabled at ends), Back link.

2.  **Static Files (`static/`):**
    *   `style.css`: Basic custom CSS for layout and card styling.
    *   `script.js` (Optional): Minimal JS for answer reveal if needed.

## Phase 4: Documentation & Refinement

1.  **README.md:** (To be created within `flashcard_app/`)
    *   Description.
    *   Prerequisites (Docker/Podman).
    *   Build instructions (`docker build ...`).
    *   Run instructions (`docker run ...` with volume mount).
    *   CSV format explanation.
2.  **Code Review & Cleanup:** Add comments, refine error handling, ensure consistency.

## Simplified Flow Diagram

```mermaid
graph TD
    A[User Accesses /] --> B{Dataset Selection Page};
    B -- Clicks Dataset --> D{/learn/dataset_id};
    B -- Uploads CSV --> C{POST /upload};
    C -- Success --> B;
    C -- Error --> B;
    D --> E{Load Progress};
    E --> F{Redirect /learn/dataset_id/card_index};
    F --> G{Flashcard Learning Page};
    G -- Clicks Next --> H{Save Progress};
    G -- Clicks Previous --> H;
    H --> F;
    G -- Clicks Card --> I{Reveal Answer};
    G -- Clicks Back --> B;

    subgraph Container
        J[Flask App: app.py]
        K[Database Logic: database.py]
        L[Templates: *.html]
        M[Static: *.css, *.js]
        N[DB File: /data/flashcard.db]
        O[Progress File: /data/progress.json]
    end

    J <--> K;
    J <--> L;
    J <--> O;
    K <--> N;