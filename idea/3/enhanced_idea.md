Subject: Implement New Features in `flashcard_app`

Based on the existing application in the `flashcard_app` folder and its corresponding `idea/*/PLAN.md`, implement the following four features:

1.  **Dataset-Level Review Initiation:** Modify the dataset listing UI to include a distinct "Review" button for each dataset entry. Clicking this button should initiate a review-specific flashcard session for that dataset.
2.  **Card Review Status and Filtering:** Implement a mechanism to mark individual cards for review (e.g., a toggle/button on the card view/edit screen). When a review session is started via the dataset "Review" button, this session must *only* contain cards from that dataset that are currently marked for review. Add a visual indicator (e.g., an icon or label) on cards that are marked for review when viewed normally or during editing.
3.  **Alphabetical Answer Choice Labels:** On the flashcard interface where multiple-choice answers are displayed, change the option labels from numerical (1, 2, 3, 4, 5) to uppercase alphabetical (A, B, C, D, E).
4.  **Answer Choice Shuffling:** For any multiple-choice question presented on the flashcard interface, randomize the display order of the answer options each time the card is shown. Ensure the correct answer is tracked accurately regardless of its shuffled position.