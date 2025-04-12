Update the flashcard application located in the `flashcard_app` folder, originally developed following `idea/1/PLAN.md`. Implement the following two features, integrating them with the existing architecture and UI:

1.  **Delete Flashcard Deck/Dataset:**
    *   Add functionality allowing users to delete an entire flashcard deck (or 'dataset').
    *   Include a user interface element (e.g., button, icon) for triggering deletion, placed appropriately (e.g., next to each deck in a list view).
    *   Implement a confirmation prompt before proceeding with the deletion (e.g., "Are you sure you want to delete '[Deck Name]'? This action cannot be undone.").
    *   On confirmation, permanently remove the selected deck and all its associated flashcards from the application's data storage.
    *   Refresh the UI to accurately reflect the deck's removal.

2.  **Persistent Notes per Flashcard:**
    *   Introduce a dedicated, editable text area (notes box) associated with each individual flashcard.
    *   Position this notes area logically within the flashcard view (e.g., below the answer field, always visible when the card is open/revealed).
    *   Ensure the notes content is saved persistently along with the flashcard's primary data (question/answer).
    *   The saved note must be displayed automatically and remain editable whenever that specific flashcard is viewed.
    *   Update the application's data model (structure used for storing flashcard data) to accommodate this new 'notes' field for each card.

Consult the existing codebase within `flashcard_app` and the details in `idea/1/PLAN.md` to understand current implementation, data structures, UI patterns, and ensure consistency with the established style.