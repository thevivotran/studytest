import os
import json
import csv
import io  # Needed for reading file stream directly
import random  # Added for shuffling choices
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    jsonify,
)  # Added jsonify
from werkzeug.utils import secure_filename  # For secure file handling
import database

# --- Configuration ---
# Define the path for the progress file within the persistent volume
DATA_DIR = "/data"
PROGRESS_FILE_PATH = os.path.join(DATA_DIR, "progress.json")
# UPLOAD_FOLDER = '/tmp' # Not strictly needed if processing in memory
ALLOWED_EXTENSIONS = {"csv"}

# --- Flask App Initialization ---
app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)  # Needed for flash messages
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
            with open(PROGRESS_FILE_PATH, "w") as f:
                json.dump({}, f)
            print(f"Created progress file at {PROGRESS_FILE_PATH}")
        except IOError as e:
            print(f"Error creating progress file {PROGRESS_FILE_PATH}: {e}")


# --- Helper Functions ---
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_progress():
    """Loads the learning progress from the JSON file."""
    try:
        with open(PROGRESS_FILE_PATH, "r") as f:
            content = f.read()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(
            f"Error loading progress file ({PROGRESS_FILE_PATH}): {e}. Returning empty progress."
        )
        return {}
    except IOError as e:
        print(
            f"Error reading progress file ({PROGRESS_FILE_PATH}): {e}. Returning empty progress."
        )
        return {}


def _save_progress_data(progress_dict):
    """Saves the entire progress dictionary to the JSON file."""
    try:
        with open(PROGRESS_FILE_PATH, "w") as f:
            json.dump(progress_dict, f, indent=4)
        return True
    except IOError as e:
        print(f"Error saving progress file ({PROGRESS_FILE_PATH}): {e}")
        return False


def save_progress(dataset_id, card_index):
    """Loads, updates, and saves the learning progress for a specific dataset."""
    progress = load_progress()
    progress[str(dataset_id)] = card_index  # Use string key for JSON compatibility
    _save_progress_data(progress)  # Use the helper to save the whole dict


# --- Routes ---
@app.route("/")
def index():
    """Displays the dataset selection page and upload form."""
    datasets = database.get_datasets()
    # Pass the template name explicitly
    return render_template("index.html", datasets=datasets)


@app.route("/upload", methods=["POST"])
def upload_file():
    """Handles CSV file upload, parsing, and database insertion."""
    if "csv_file" not in request.files:
        flash("No file part in the request.", "danger")
        return redirect(url_for("index"))

    file = request.files["csv_file"]
    dataset_name = request.form.get("dataset_name", "").strip()

    # --- Input Validation ---
    if not dataset_name:
        flash("Dataset name cannot be empty.", "danger")
        return redirect(url_for("index"))

    if database.get_dataset_id_by_name(dataset_name) is not None:
        flash(
            f"Dataset name '{dataset_name}' already exists. Please choose a unique name.",
            "danger",
        )
        return redirect(url_for("index"))

    if file.filename == "":
        flash("No file selected for uploading.", "danger")
        return redirect(url_for("index"))

    if not file or not allowed_file(file.filename):
        flash("Invalid file type. Only .csv files are allowed.", "danger")
        return redirect(url_for("index"))

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
                print(len(row))
                raise ValueError(
                    f"Incorrect number of columns ({len(row)}) on line {line_num}. Expected 6 or 7."
                )

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
                raise ValueError(
                    f"Missing required data (question, answer, or choices 1-4) on line {line_num}."
                )

            cards_to_add.append(
                {
                    "question": question,
                    "correct_answer": correct_answer,
                    "choice1": choice1,
                    "choice2": choice2,
                    "choice3": choice3,
                    "choice4": choice4,
                    "choice5": choice5,
                    # Notes will be added with default empty string by database.add_card
                }
            )

        if not cards_to_add:
            raise ValueError("CSV file is empty or contains no valid data rows.")

        # --- Add to Database ---
        dataset_id = database.add_dataset(dataset_name)
        if dataset_id is None:
            # Should have been caught earlier, but double-check
            flash(
                f"Failed to create dataset '{dataset_name}'. It might already exist.",
                "danger",
            )
            return redirect(url_for("index"))

        added_count = 0
        # Consider using a transaction in database.py for bulk inserts
        for card_data in cards_to_add:
            # database.add_card now handles the 'notes' field internally with a default
            if database.add_card(dataset_id=dataset_id, **card_data):
                added_count += 1
            else:
                # Rollback or cleanup might be needed here in a more complex scenario
                flash(f"Error adding card: {card_data['question'][:30]}...", "danger")
                # Optionally delete the partially added dataset? For now, just report error.
                # Consider deleting the dataset if card adding fails mid-way
                # database.delete_dataset(dataset_id) # Example cleanup
                return redirect(url_for("index"))

        flash(
            f"Successfully uploaded dataset '{dataset_name}' with {added_count} cards.",
            "success",
        )

    except UnicodeDecodeError:
        flash("Error decoding file. Please ensure the file is UTF-8 encoded.", "danger")
    except csv.Error as e:
        flash(f"Error parsing CSV file: {e}", "danger")
    except ValueError as e:
        flash(f"Error processing CSV data: {e}", "danger")
    except Exception as e:
        # Catch unexpected errors
        flash(f"An unexpected error occurred during upload: {e}", "danger")
        print(f"Unexpected upload error: {e}")  # Log for debugging

    return redirect(url_for("index"))


# --- Learning and Review Routes ---


@app.route("/learn/<int:dataset_id>")
def learn_dataset(dataset_id):
    """Loads progress and redirects to the specific card index for learning."""
    progress = load_progress()
    # Get last viewed index for this dataset, default to 0
    last_index = progress.get(str(dataset_id), 0)

    # Validate that the dataset actually exists and has cards before redirecting
    # Use get_cards_by_dataset for the initial check, even if review mode might use a different set later
    cards = database.get_cards_by_dataset(dataset_id)
    if not cards:
        flash(f"Dataset {dataset_id} not found or is empty.", "warning")
        return redirect(url_for("index"))

    # Ensure last_index is within bounds of the *full* dataset, redirect to 0 if not
    if not (0 <= last_index < len(cards)):
        print(
            f"Warning: Invalid progress index {last_index} for dataset {dataset_id}. Resetting to 0."
        )
        last_index = 0
        save_progress(dataset_id, last_index)  # Correct the saved progress

    # Redirect to the first card in normal learn mode
    return redirect(
        url_for("show_card", dataset_id=dataset_id, card_index=last_index, mode="learn")
    )


@app.route("/review/<int:dataset_id>")
def review_dataset(dataset_id):
    """Initiates a review session for the marked cards in a dataset."""
    review_cards = database.get_review_cards_by_dataset(dataset_id)

    if not review_cards:
        flash(f"No cards marked for review in dataset {dataset_id}.", "info")
        return redirect(url_for("index"))

    # Redirect to the first card in review mode
    # card_index is 0 because we start from the beginning of the *review* list
    return redirect(
        url_for("show_card", dataset_id=dataset_id, card_index=0, mode="review")
    )


@app.route("/learn/<int:dataset_id>/<int:card_index>")
@app.route("/learn/<int:dataset_id>/<int:card_index>/<mode>")  # Add mode to route
def show_card(dataset_id, card_index, mode="learn"):  # Default to learn mode
    """Displays a specific flashcard for the given dataset and index, handling learn/review modes."""

    # --- Fetch Dataset Info ---
    dataset = database.get_dataset_by_id(dataset_id)
    if not dataset:
        flash(f"Dataset with ID {dataset_id} not found.", "danger")
        return redirect(url_for("index"))
    dataset_name = dataset["name"] # Get name from the dataset row

    # --- Fetch Cards based on Mode ---
    is_review_mode = mode == "review"
    if is_review_mode:
        cards = database.get_review_cards_by_dataset(dataset_id)
        if not cards:
            flash(
                f"No cards marked for review in dataset '{dataset_name}'. Returning to index.",
                "info",
            )
            return redirect(url_for("index"))
    else:  # Learn mode
        cards = database.get_cards_by_dataset(dataset_id)
        if not cards:
            # This case should ideally be caught by learn_dataset, but check again
            flash(f"Dataset '{dataset_name}' is empty.", "warning")
            return redirect(url_for("index"))

    total_cards = len(cards)

    # --- Validate card_index ---
    if not (0 <= card_index < total_cards):
        flash(
            f"Invalid card index ({card_index}) for {mode} mode in dataset '{dataset_name}'. Showing first card instead.",
            "warning",
        )
        # Redirect to the first card of this dataset *in the current mode*
        return redirect(
            url_for("show_card", dataset_id=dataset_id, card_index=0, mode=mode)
        )

    # Get the current card from the correct list
    current_card = cards[card_index]

    # Save progress ONLY if in learn mode
    if not is_review_mode:
        save_progress(dataset_id, card_index)

    # --- Prepare Choices for Shuffling ---
    choices = [
        current_card["choice1"],
        current_card["choice2"],
        current_card["choice3"],
        current_card["choice4"],
    ]
    if current_card["choice5"]:
        choices.append(current_card["choice5"])

    # Filter out any potentially empty choices just in case
    choices = [choice for choice in choices if choice and choice.strip()]

    # Shuffle the choices
    shuffled_choices = choices[:]  # Create a copy before shuffling
    random.shuffle(shuffled_choices)

    # --- Render Template ---
    return render_template(
        "learn.html",
        card=current_card,
        dataset_id=dataset_id,
        dataset_name=dataset_name, # Pass dataset name
        current_index=card_index,
        total_cards=total_cards,
        mode=mode,
        shuffled_choices=shuffled_choices,
    )


# --- Other Routes (Deletion, Notes, Review Toggle) ---


@app.route("/delete_dataset/<int:dataset_id>", methods=["POST"])
def delete_dataset(dataset_id):
    """Deletes a dataset and its associated progress."""
    if database.delete_dataset(dataset_id):
        # Remove progress for this dataset
        progress = load_progress()
        dataset_id_str = str(dataset_id)
        if dataset_id_str in progress:
            del progress[dataset_id_str]
            if not _save_progress_data(progress):
                flash("Dataset deleted, but failed to update progress file.", "warning")
            else:
                flash(f"Dataset {dataset_id} deleted successfully.", "success")
        else:
            flash(
                f"Dataset {dataset_id} deleted successfully (no progress data found).",
                "success",
            )
    else:
        flash(f"Error deleting dataset {dataset_id}. It might not exist.", "danger")

    return redirect(url_for("index"))


@app.route("/update_note/<int:card_id>", methods=["POST"])
def update_note(card_id):
    """Updates the notes for a specific card via AJAX."""
    notes = request.form.get("notes")
    if notes is None:
        data = request.get_json()
        if data and "notes" in data:
            notes = data["notes"]
        else:
            return jsonify({"status": "error", "message": "Missing notes data"}), 400

    if database.update_card_notes(card_id, notes):
        return jsonify({"status": "success"})
    else:
        return jsonify(
            {"status": "error", "message": "Failed to update notes in database"}
        ), 500


@app.route("/toggle_review/<int:card_id>", methods=["POST"])
def toggle_review(card_id):
    """Toggles the review status for a specific card via AJAX."""
    if database.toggle_card_review_status(card_id):
        return jsonify({"status": "success"})
    else:
        # Card not found or DB error
        return jsonify(
            {"status": "error", "message": "Failed to toggle review status"}
        ), 500


# --- Main Execution ---
if __name__ == "__main__":
    # Note: Use 'flask run' command instead of running this directly for development server
    # The Dockerfile uses 'flask run'
    print(
        "To run the app, use the command: flask run --debug"
    )  # Added --debug for development
