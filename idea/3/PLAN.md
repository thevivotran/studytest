# Plan: Implement New Features in `flashcard_app`

**Overall Goal:** Enhance the `flashcard_app` with dataset-specific review sessions, card review marking, alphabetical choice labels, and answer shuffling.

**Phase 1: Database Schema Modification & Backend Logic for Review Status**

1.  **Modify `database.py`:**
    *   **Add `mark_for_review` column:** Update `init_db` to add a `mark_for_review` column (BOOLEAN, defaulting to FALSE) to the `cards` table. Ensure this migration is handled gracefully.
    *   **Update `add_card`:** Modify the `add_card` function to accept and insert the `mark_for_review` status (defaulting to `False`).
    *   **Create `get_review_cards_by_dataset`:** Add a new function `get_review_cards_by_dataset(dataset_id)` that retrieves only cards where `mark_for_review` is TRUE for a given `dataset_id`.
    *   **Create `toggle_card_review_status`:** Add a function `toggle_card_review_status(card_id)` that flips the boolean value of `mark_for_review` for a specific card ID.

    ```mermaid
    graph TD
        subgraph Database Schema (cards table)
            id[id INTEGER PK]
            dataset_id[dataset_id INTEGER FK]
            question[question TEXT]
            correct_answer[correct_answer TEXT]
            choice1[choice1 TEXT]
            choice2[choice2 TEXT]
            choice3[choice3 TEXT]
            choice4[choice4 TEXT]
            choice5[choice5 TEXT]
            notes[notes TEXT]
            mark_for_review[mark_for_review BOOLEAN DEFAULT FALSE] -- Added --> id
        end
    ```

2.  **Modify `app.py`:**
    *   **Add `/toggle_review/<int:card_id>` route:** Create a new POST route that calls `database.toggle_card_review_status(card_id)`. This route should return JSON status (success/error).

**Phase 2: Frontend for Review Status & Dataset Review Initiation**

1.  **Modify `templates/learn.html`:**
    *   **Add Review Toggle:** Add a button or checkbox (e.g., "Mark for Review") to the card view.
    *   **Add JavaScript:** Implement JavaScript to call the `/toggle_review/<int:card_id>` endpoint via AJAX when the toggle button/checkbox is clicked. Update the UI accordingly on success.
    *   **Add Visual Indicator:** Display a clear visual indicator (e.g., a small icon or text like "[Review]") next to the question or card title if `card.mark_for_review` is true.

2.  **Modify `templates/index.html`:**
    *   **Add "Review" Button:** For each dataset listed, add a "Review" button alongside the existing "Learn" and "Delete" buttons. This button should link to `/review/{{ dataset.id }}`.

3.  **Modify `app.py`:**
    *   **Add `/review/<int:dataset_id>` route:** Create this new route. It should:
        *   Call `database.get_review_cards_by_dataset(dataset_id)`.
        *   If no review cards are found, flash a message and redirect to `index`.
        *   If review cards exist, redirect to `/learn/{{ dataset_id }}/0?mode=review`.
    *   **Modify `show_card`:**
        *   Check for the `mode=review` query parameter.
        *   If `mode=review` is present:
            *   Fetch cards using `get_review_cards_by_dataset`.
            *   Disable progress saving (`save_progress`).
        *   Navigation (Next/Previous) within `learn.html` needs to respect this mode (pass `mode=review` in links).

    ```mermaid
    graph LR
        A[User Clicks 'Review' on Dataset List] --> B{Route: /review/<dataset_id>};
        B --> C{app.py: Fetch review cards};
        C -- Cards Found --> D{Redirect to /learn/<dataset_id>/0?mode=review};
        C -- No Cards Found --> E{Redirect to Index with Message};
        D --> F{Route: /learn/<dataset_id>/<card_index>?mode=review};
        F --> G{app.py: show_card (review mode)};
        G --> H{Fetch card using get_review_cards_by_dataset};
        H --> I[Render learn.html (review context)];
    ```

**Phase 3: Alphabetical Labels & Answer Shuffling**

1.  **Modify `app.py` (`show_card` function):**
    *   **Gather Choices:** Before rendering, collect all answer choices (`correct_answer`, `choice1` to `choice5` if it exists) into a list. Store the original `correct_answer` separately.
    *   **Shuffle Choices:** Use Python's `random.shuffle` to randomize the order of the choices list.
    *   **Pass Shuffled Data:** Pass the shuffled list of choices and the original `correct_answer` to the template.

2.  **Modify `templates/learn.html`:**
    *   **Display Shuffled Choices:** Iterate through the shuffled choices list provided by the backend.
    *   **Assign Alphabetical Labels:** Assign labels A, B, C, D, E dynamically during the loop (e.g., using `loop.index` in Jinja2).
    *   **Handle Answer Submission:** Ensure the submitted answer correctly identifies the chosen *text*, which the backend can then compare against the stored original `correct_answer`.

**Summary of Changes:**

*   **`database.py`:** Add `mark_for_review` column, `get_review_cards_by_dataset`, `toggle_card_review_status` functions. Update `init_db`, `add_card`.
*   **`app.py`:** Add `/toggle_review/<int:card_id>` and `/review/<int:dataset_id>` routes. Modify `show_card` to handle review mode, shuffling, and disable progress saving in review mode.
*   **`templates/index.html`:** Add "Review" button per dataset.
*   **`templates/learn.html`:** Add review toggle button/checkbox, visual indicator for review cards, AJAX for toggling, display alphabetical/shuffled choices, adjust answer submission logic.