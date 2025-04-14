# Plan: Remove "Previous" Button on First Card

**Task:** Prevent users from navigating to a negative card index on the learn page by removing the "Previous" button when they are on the first card (`current_index == 0`).

**Analysis:**

*   The "Previous" button is located in `flashcard_app/templates/learn.html` (lines 20-26).
*   Currently, it uses a Jinja condition (`{% if current_index == 0 %}disabled{% endif %}`) to add a `disabled` class.
*   The corresponding JavaScript (`flashcard_app/static/learn.js`) handles keyboard navigation (Left Arrow) and checks if the button exists and is *not* disabled.
*   Simply removing the button element entirely when `current_index == 0` is safe and compatible with the existing JavaScript.

**Implementation Steps:**

1.  **Modify `flashcard_app/templates/learn.html`:**
    *   Wrap the entire `<li>...</li>` block containing the "Previous" button link with a Jinja conditional statement: `{% if current_index > 0 %}`.
    *   Remove the `{% if current_index == 0 %}disabled{% endif %}` part from the `<a>` tag's class attribute within the list item.

**Proposed Change (Diff):**

```diff
--- a/flashcard_app/templates/learn.html
+++ b/flashcard_app/templates/learn.html
@@ -17,14 +17,14 @@

     {# Navigation - Using nav element #}
     <nav class="navigation">
+        {% if current_index > 0 %} {# <-- Add this condition #}
         <ul>
             <li>
                 {# Use role="button" for Pico styling on links #}
                 <a href="{{ url_for('show_card', dataset_id=dataset_id, card_index=current_index - 1, mode=mode) }}"
-                    role="button" class="secondary {% if current_index == 0 %}disabled{% endif %}"> {# Pico secondary style #}
+                    role="button" class="secondary"> {# <-- Remove disabled class logic #}
                     &laquo; Previous
                 </a>
             </li>
         </ul>
+        {% endif %} {# <-- End condition #}
         <ul>
             <li><ins class="card-counter">Card {{ current_index + 1 }} of {{ total_cards }}</ins></li> {# Pico <ins> for inline text #}
         </ul>

```

**Next Step:** Switch to Code mode to implement this change.