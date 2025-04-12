import os
import json
import csv
import io # Needed for reading file stream directly
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from werkzeug.utils import secure_filename # For secure file handling
import database

# --- Configuration ---
# Define the path for the progress file within the persistent volume
DATA_DIR = '/data'
PROGRESS_FILE_PATH = os.path.join(DATA_DIR, 'progress.json')
# UPLOAD_FOLDER = '/tmp' # Not strictly needed if processing in memory
ALLOWED_EXTENSIONS = {'csv'}

# --- Flask App Initialization ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # Needed for flash messages
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Not saving files persistently here

# --- Database Initialization ---
# Ensure the database is initialized when the application starts
with app.app_context():
    print("Initializing Database from app.py...")
    database.init_db()
    # Ensure the /data directory exists for progress file
    os.makedirs(DATA_DIR, exist_ok=True)
    # Ensure the progress file exists, create if not
    if not os.path.exists(PROGRESS_FILE_PATH):
        try:
            with open(PROGRESS_FILE_PATH, 'w') as f:
                json.dump({}, f)
            print(f"Created progress file at {PROGRESS_FILE_PATH}")
        except IOError as e:
            print(f"Error creating progress file {PROGRESS_FILE_PATH}: {e}")


# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_progress():
    """Loads the learning progress from the JSON file."""
    try:
        with open(PROGRESS_FILE_PATH, 'r') as f:
            content = f.read()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading progress file ({PROGRESS_FILE_PATH}): {e}. Returning empty progress.")
        return {}
    except IOError as e:
        print(f"Error reading progress file ({PROGRESS_FILE_PATH}): {e}. Returning empty progress.")
        return {}


def save_progress(dataset_id, card_index):
    """Saves the learning progress for a specific dataset."""
    progress = load_progress()
    progress[str(dataset_id)] = card_index # Use string key for JSON compatibility
    try:
        with open(PROGRESS_FILE_PATH, 'w') as f:
            json.dump(progress, f, indent=4)
    except IOError as e:
        print(f"Error saving progress file ({PROGRESS_FILE_PATH}): {e}")


# --- Routes ---
@app.route('/')
def index():
    """Displays the dataset selection page and upload form."""
    datasets = database.get_datasets()
    # Pass the template name explicitly
    return render_template('index.html', datasets=datasets)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles CSV file upload, parsing, and database insertion."""
    if 'csv_file' not in request.files:
        flash('No file part in the request.', 'danger')
        return redirect(url_for('index'))

    file = request.files['csv_file']
    dataset_name = request.form.get('dataset_name', '').strip()

    # --- Input Validation ---
    if not dataset_name:
        flash('Dataset name cannot be empty.', 'danger')
        return redirect(url_for('index'))

    if database.get_dataset_id_by_name(dataset_name) is not None:
        flash(f"Dataset name '{dataset_name}' already exists. Please choose a unique name.", 'danger')
        return redirect(url_for('index'))

    if file.filename == '':
        flash('No file selected for uploading.', 'danger')
        return redirect(url_for('index'))

    if not file or not allowed_file(file.filename):
        flash('Invalid file type. Only .csv files are allowed.', 'danger')
        return redirect(url_for('index'))

    # --- CSV Parsing and Database Insertion ---
    try:
        # Read the file stream directly without saving temporarily
        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        csv_reader = csv.reader(stream)

        cards_to_add = []
        line_num = 0
        for row in csv_reader:
            line_num += 1
            # Expecting 6 or 7 columns: question, correct_answer, choice1-4, [choice5]
            if not (6 <= len(row) <= 7):
                raise ValueError(f"Incorrect number of columns ({len(row)}) on line {line_num}. Expected 6 or 7.")

            # Extract data, handle optional 7th column
            question = row[0].strip()
            correct_answer = row[1].strip()
            choice1 = row[2].strip()
            choice2 = row[3].strip()
            choice3 = row[4].strip()
            choice4 = row[5].strip()
            choice5 = row[6].strip() if len(row) == 7 else None

            # Basic validation (ensure required fields are not empty)
            if not all([question, correct_answer, choice1, choice2, choice3, choice4]):
                 raise ValueError(f"Missing required data (question, answer, or choices 1-4) on line {line_num}.")

            cards_to_add.append({
                "question": question,
                "correct_answer": correct_answer,
                "choice1": choice1,
                "choice2": choice2,
                "choice3": choice3,
                "choice4": choice4,
                "choice5": choice5
            })

        if not cards_to_add:
             raise ValueError("CSV file is empty or contains no valid data rows.")

        # --- Add to Database ---
        dataset_id = database.add_dataset(dataset_name)
        if dataset_id is None:
            # Should have been caught earlier, but double-check
            flash(f"Failed to create dataset '{dataset_name}'. It might already exist.", 'danger')
            return redirect(url_for('index'))

        added_count = 0
        # Consider using a transaction in database.py for bulk inserts
        for card_data in cards_to_add:
            if database.add_card(dataset_id=dataset_id, **card_data):
                added_count += 1
            else:
                # Rollback or cleanup might be needed here in a more complex scenario
                flash(f"Error adding card: {card_data['question'][:30]}...", 'danger')
                # Optionally delete the partially added dataset? For now, just report error.
                return redirect(url_for('index'))

        flash(f"Successfully uploaded dataset '{dataset_name}' with {added_count} cards.", 'success')

    except UnicodeDecodeError:
        flash('Error decoding file. Please ensure the file is UTF-8 encoded.', 'danger')
    except csv.Error as e:
        flash(f'Error parsing CSV file: {e}', 'danger')
    except ValueError as e:
        flash(f'Error processing CSV data: {e}', 'danger')
    except Exception as e:
        # Catch unexpected errors
        flash(f'An unexpected error occurred during upload: {e}', 'danger')
        print(f"Unexpected upload error: {e}") # Log for debugging

    return redirect(url_for('index'))


# --- Learning Routes ---

@app.route('/learn/<int:dataset_id>')
def learn_dataset(dataset_id):
    """Loads progress and redirects to the specific card index for learning."""
    progress = load_progress()
    # Get last viewed index for this dataset, default to 0
    # Use string key for dataset_id when accessing progress dict
    last_index = progress.get(str(dataset_id), 0)

    # Validate that the dataset actually exists and has cards before redirecting
    cards = database.get_cards_by_dataset(dataset_id)
    if not cards:
        flash(f"Dataset {dataset_id} not found or is empty.", "warning")
        return redirect(url_for('index'))

    # Ensure last_index is within bounds, redirect to 0 if not
    if not (0 <= last_index < len(cards)):
        print(f"Warning: Invalid progress index {last_index} for dataset {dataset_id}. Resetting to 0.")
        last_index = 0
        save_progress(dataset_id, last_index) # Correct the saved progress

    return redirect(url_for('show_card', dataset_id=dataset_id, card_index=last_index))


@app.route('/learn/<int:dataset_id>/<int:card_index>')
def show_card(dataset_id, card_index):
    """Displays a specific flashcard for the given dataset and index."""
    cards = database.get_cards_by_dataset(dataset_id)

    if not cards:
        flash(f"Dataset {dataset_id} not found or is empty.", "warning")
        return redirect(url_for('index'))

    total_cards = len(cards)

    # Validate card_index bounds
    if not (0 <= card_index < total_cards):
        flash(f"Invalid card index ({card_index}). Showing first card instead.", "warning")
        # Redirect to the first card of this dataset
        return redirect(url_for('show_card', dataset_id=dataset_id, card_index=0))

    # Get the current card
    current_card = cards[card_index]

    # Save progress *after* validation and fetching the card
    save_progress(dataset_id, card_index)

    # Pass necessary data to the template
    return render_template('learn.html',
                           card=current_card,
                           dataset_id=dataset_id,
                           current_index=card_index,
                           total_cards=total_cards)


# --- Main Execution ---
if __name__ == '__main__':
    # Note: Use 'flask run' command instead of running this directly for development server
    # The Dockerfile uses 'flask run'
    print("To run the app, use the command: flask run")