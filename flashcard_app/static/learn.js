function toggleAnswer() {
    const cardElement = document.getElementById('card-container');
    cardElement.classList.toggle('show-answer');
}

// --- Notes Auto-Save Logic ---
const notesTextarea = document.getElementById('card-notes');
const notesStatus = document.getElementById('notes-status');
let saveTimeout;

// Check if notesTextarea exists before adding listener
if (notesTextarea) {
    notesTextarea.addEventListener('blur', function() {
        const cardId = this.dataset.cardId;
        const notesContent = this.value;

        clearTimeout(saveTimeout);
        notesStatus.textContent = 'Saving...';
        notesStatus.style.color = 'orange';

        const formData = new FormData();
        formData.append('notes', notesContent);

        fetch(`/update_note/${cardId}`, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.message || `HTTP error! status: ${response.status}`) });
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                notesStatus.textContent = 'Saved';
                notesStatus.style.color = 'green';
            } else {
                throw new Error(data.message || 'Unknown error saving notes.');
            }
        })
        .catch(error => {
            console.error('Error saving notes:', error);
            notesStatus.textContent = 'Error saving!';
            notesStatus.style.color = 'red';
        })
        .finally(() => {
            saveTimeout = setTimeout(() => {
                notesStatus.textContent = '';
            }, 3000);
        });
    });
}
// --- End Notes Auto-Save Logic ---

// --- Review Toggle Logic ---
const reviewStatus = document.getElementById('review-status');
const reviewIndicator = document.getElementById('review-indicator');
const reviewToggleButton = document.getElementById('review-toggle-button'); // Get button for event listener
let reviewTimeout;

// Check if reviewToggleButton exists before adding listener
if (reviewToggleButton) {
    // Note: The onclick attribute is removed from the HTML later.
    // We add the listener here instead.
    reviewToggleButton.addEventListener('click', function() {
        toggleReviewStatus(this); // Pass the button element itself
    });
}

function toggleReviewStatus(button) {
    const cardId = button.dataset.cardId;

    clearTimeout(reviewTimeout);
    // Check if reviewStatus exists before manipulating
    if (reviewStatus) {
        reviewStatus.textContent = 'Updating...';
        reviewStatus.style.color = 'orange';
    }


    fetch(`/toggle_review/${cardId}`, {
        method: 'POST'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.message || `HTTP error! status: ${response.status}`) });
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            button.classList.toggle('marked');
            const newIsMarked = button.classList.contains('marked');
            button.textContent = newIsMarked ? 'Unmark for Review' : 'Mark for Review';

            // Toggle visual indicator class if it exists
            if (reviewIndicator) {
                reviewIndicator.classList.toggle('visible', newIsMarked);
            }

            if (reviewStatus) {
                reviewStatus.textContent = 'Status updated';
                reviewStatus.style.color = 'green';
            }
        } else {
            throw new Error(data.message || 'Unknown error toggling review status.');
        }
    })
    .catch(error => {
        console.error('Error toggling review status:', error);
        if (reviewStatus) {
            reviewStatus.textContent = 'Error updating!';
            reviewStatus.style.color = 'red';
        }
    })
    .finally(() => {
        // Check if reviewStatus exists before setting timeout
        if (reviewStatus) {
            reviewTimeout = setTimeout(() => {
                reviewStatus.textContent = '';
            }, 3000);
        }
    });
}
// --- End Review Toggle Logic ---

// --- Keyboard Navigation ---
// Add this event listener to the document
document.addEventListener('keydown', function(event) {
    // Ensure we are on the learn page by checking for a specific element
    if (!document.getElementById('card-container')) {
        return; // Exit if not on the learn page
    }

    // Prevent default behavior for spacebar if needed (e.g., scrolling)
    if (event.code === 'Space') {
        event.preventDefault();
        toggleAnswer();
    } else if (event.code === 'ArrowLeft') {
        // Updated selector for Previous button
        const prevButton = document.querySelector('.navigation ul:first-of-type a');
        if (prevButton && !prevButton.classList.contains('disabled')) {
            window.location.href = prevButton.href; // Navigate
        }
    } else if (event.code === 'ArrowRight') {
        // Updated selector for Next button
        const nextButton = document.querySelector('.navigation ul:last-of-type a');
        if (nextButton && !nextButton.classList.contains('disabled')) {
            window.location.href = nextButton.href; // Navigate
        }
    }
});
// --- End Keyboard Navigation ---