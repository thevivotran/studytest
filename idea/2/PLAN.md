## Flashcard Application Enhancement Plan (Final)

**Objective:** Enhance the Flask flashcard application by adding "Delete Deck" and "Persistent Card Notes" features.

### Feature 1: Delete Flashcard Deck/Dataset

*   **Database (`database.py`):**
    *   Add `delete_dataset(dataset_id)` function (using `DELETE FROM datasets WHERE id = ?`). Relies on existing `ON DELETE CASCADE` for cards.
*   **Backend (`app.py`):**
    *   Add `POST` route `/delete_dataset/<int:dataset_id>`.
    *   Calls `database.delete_dataset()`.
    *   Removes the corresponding `dataset_id` key from the `progress.json` data.
    *   Requires refining `save_progress` or adding a helper `_save_progress_data(progress_dict)` to save the modified progress dictionary.
    *   Flashes success/error message.
    *   Redirects to index (`/`).
*   **Frontend (`templates/index.html`):**
    *   Add a simple text **"Delete" button** next to each dataset.
    *   Wrap the button in a small `<form>` making a `POST` request to the delete route.
    *   Include `onsubmit="return confirm(...)"` in the form for user confirmation.

### Feature 2: Persistent Notes per Flashcard

*   **Database (`database.py`):**
    *   Add `notes TEXT` column to `cards` table (update `init_db` to handle this idempotently using `ALTER TABLE ... ADD COLUMN ...`).
    *   Update `add_card` function signature and `INSERT` statement for the new `notes` column.
    *   Ensure `get_cards_by_dataset` selects the `notes` column (`SELECT *` works, but explicit is better).
    *   Add `update_card_notes(card_id, notes)` function (using `UPDATE cards SET notes = ? WHERE id = ?`).
*   **Backend (`app.py`):**
    *   Add `POST` route `/update_note/<int:card_id>`.
    *   Gets `notes` from request form data.
    *   Calls `database.update_card_notes()`.
    *   Returns JSON status (`{'status': 'success'}` or `{'status': 'error', ...}`).
*   **Frontend (`templates/learn.html`):**
    *   Add a `<textarea id="card-notes" data-card-id="{{ card.id }}">` below the answer area.
    *   Populate textarea with `{{ card.notes if card.notes else '' }}`.
    *   Add a small status indicator span (`<span id="notes-status">`).
*   **JavaScript (Inline `<script>` in `learn.html` or `static/script.js`):**
    *   Add `blur` event listener to the `#card-notes` textarea.
    *   On `blur`:
        *   Get `card_id` from `data-card-id` attribute.
        *   Get textarea content.
        *   Send async `POST` request via `fetch` to `/update_note/<card_id>` with notes data.
        *   Update `#notes-status` based on the JSON response (e.g., "Saving...", "Saved", "Error").

### Conceptual Flow Diagram

```mermaid
graph TD
    subgraph Feature 1: Delete Deck
        U1[User Clicks 'Delete' Button] --> JS1{JS Confirm Dialog};
        JS1 -- Yes --> FE1[POST /delete_dataset/<id>];
        FE1 --> BE1[app.py: /delete_dataset route];
        BE1 --> DB1[database.py: delete_dataset(id)];
        DB1 -- "Deletes Dataset & Cards (Cascade)" --> BE1;
        BE1 --> UP1[Update progress.json];
        UP1 --> BE1;
        BE1 -- Flashes Success/Error --> FE2[Redirect to /];
    end

    subgraph Feature 2: Persistent Notes
        U2[User Views Card] --> FE3[learn.html: Renders card + notes textarea];
        FE3 --> U3[User Edits Notes];
        U3 -- Clicks Away (blur) --> JS2{JS 'blur' Event Listener};
        JS2 --> FE4[Async POST /update_note/<card_id>];
        FE4 --> BE2[app.py: /update_note route];
        BE2 --> DB2[database.py: update_card_notes(id, notes)];
        DB2 -- Updates DB --> BE2;
        BE2 --> FE5[Return JSON status];
        FE5 --> JS3{JS Updates Status Indicator};

        DB3[database.py: init_db] -- Adds 'notes' column --> DB4[cards table];
        DB5[database.py: add_card] -- Includes 'notes' --> DB4;
        DB6[database.py: get_cards_by_dataset] -- Selects 'notes' --> BE3[app.py: /learn route];
        BE3 --> FE3;
    end
```
