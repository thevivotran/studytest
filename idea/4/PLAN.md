# Plan: UI Update with Pico.css (Prioritizing Learn Page with Keyboard Nav)

This plan outlines the steps to update the Flashcard App UI using the Pico.css framework, with a focus on improving the flashcard learning page (`learn.html`) and adding keyboard navigation.

## 1. Integrate Pico.css

*   **Action:** Add the Pico.css framework to the project.
*   **Method:** Link the Pico.css CDN or download/host it locally.
*   **Location:** Update `<head>` in `flashcard_app/templates/base.html`.

## 2. Refactor `learn.html` Code

*   **Goal:** Separate inline styles and scripts for better organization and maintainability.
*   **Actions:**
    *   Create `flashcard_app/static/learn.css`: Move CSS rules from inline `<style>` block.
    *   Create `flashcard_app/static/learn.js`: Move JavaScript from inline `<script>` block.
    *   Update `learn.html`: Remove inline blocks and link the new external files (`learn.css` in `{% block head_extra %}`, `learn.js` in `{% block scripts %}`).

## 3. Adapt Styles to Pico.css

*   **Goal:** Ensure existing styles work harmoniously with Pico.css and remove redundant rules.
*   **Actions:**
    *   Review `flashcard_app/static/style.css` and `flashcard_app/static/learn.css`.
    *   **Remove Redundancy:** Delete CSS rules now handled by Pico.css (e.g., basic body, typography, buttons, forms, container).
    *   **Harmonize:** Adjust remaining custom styles (flashcard layout, answer visibility, notes, review toggle, navigation, alerts) to align with Pico's classless approach and aesthetic. Leverage semantic HTML.

## 4. Enhance `learn.html` UI (Priority)

*   **Goal:** Modernize the flashcard interface and improve usability.
*   **Actions:**
    *   **Flashcard Layout:** Structure content using Pico.css conventions (e.g., `<article>`). Improve spacing and readability.
    *   **Navigation & Feedback:** Style Previous/Next buttons and counter using Pico defaults. Make "Saving..."/"Saved" feedback more subtle and integrated.
    *   **Keyboard Navigation:** Implement JavaScript in `learn.js` for:
        *   Left Arrow Key: Previous card.
        *   Right Arrow Key: Next card.
        *   Spacebar: Toggle answer visibility.
    *   **Responsiveness:** Verify layout adaptation on smaller screens using Pico's built-in capabilities.

## 5. Update `index.html` UI

*   **Goal:** Ensure the index page aligns with the new Pico.css styling.
*   **Actions:**
    *   Review upload form and dataset list styling (most should be handled by Pico).
    *   Adjust margins/structure if needed.
    *   Ensure buttons (`Upload`, `Review Marked`, `Delete`) use Pico defaults.

## 6. Testing

*   **Goal:** Ensure the updated UI is functional, visually correct, and usable.
*   **Actions:**
    *   Test `index.html` and `learn.html` thoroughly.
    *   Verify all functionalities: upload, navigation, answer reveal, notes saving, review toggle, **keyboard navigation**.
    *   Check appearance and usability across different browsers and screen sizes.
    *   Test both light and dark modes provided by Pico.css.

## Visual Plan (Mermaid Diagram)

```mermaid
graph TD
    subgraph Setup & Refactor
        A[Add Pico.css Link to base.html] --> B(Create learn.css from inline style);
        A --> C(Create learn.js from inline script);
        B --> D(Link learn.css in learn.html);
        C --> E(Link learn.js in learn.html);
    end

    subgraph Styling & Enhancement
        F[Clean style.css (Remove Pico overlaps)] --> G[Adapt learn.css (Harmonize with Pico)];
        G --> H[Enhance Flashcard Layout/Style & Add Keyboard Nav (learn.html)];
        H --> I[Style Navigation & Feedback (learn.html)];
        F --> J[Adapt Index Page Styles (index.html)];
    end

    subgraph Finalization
        I --> K[Test Thoroughly (All Pages, Responsive, Modes, Keyboard Nav)];
        J --> K;
    end

    E --> G;
    D --> G;