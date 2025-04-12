import sqlite3
import os

# Define the path for the database file within the persistent volume
DATABASE_DIR = "/data"
DATABASE_PATH = os.path.join(DATABASE_DIR, "flashcard.db")


def get_db_connection():
    """Establishes a connection to the SQLite database."""
    # Ensure the /data directory exists (important for the first run)
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    # Return rows as dictionary-like objects
    conn.row_factory = sqlite3.Row
    # Enable foreign key constraint enforcement (good practice)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _table_has_column(cursor, table_name, column_name):
    """Checks if a table has a specific column."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    return column_name in columns


def init_db():
    """Initializes the database by creating tables and adding columns if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Create datasets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)

        # Create cards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                choice1 TEXT NOT NULL,
                choice2 TEXT NOT NULL,
                choice3 TEXT NOT NULL,
                choice4 TEXT NOT NULL,
                choice5 TEXT,
                FOREIGN KEY (dataset_id) REFERENCES datasets (id) ON DELETE CASCADE
            )
        """)

        # Add 'notes' column to cards table if it doesn't exist
        if not _table_has_column(cursor, "cards", "notes"):
            print("Adding 'notes' column to 'cards' table...")
            cursor.execute("ALTER TABLE cards ADD COLUMN notes TEXT")
            print("'notes' column added.")
        else:
            print("'notes' column already exists in 'cards' table.")

        # Add 'mark_for_review' column to cards table if it doesn't exist
        if not _table_has_column(cursor, "cards", "mark_for_review"):
            print("Adding 'mark_for_review' column to 'cards' table...")
            # Add column with default value FALSE (0 for SQLite BOOLEAN)
            cursor.execute(
                "ALTER TABLE cards ADD COLUMN mark_for_review BOOLEAN DEFAULT 0"
            )
            print("'mark_for_review' column added.")
        else:
            print("'mark_for_review' column already exists in 'cards' table.")

        conn.commit()
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        conn.rollback()  # Rollback changes on error
    finally:
        conn.close()


def add_dataset(name):
    """Adds a new dataset to the database. Returns the new dataset ID or None if name exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO datasets (name) VALUES (?)", (name,))
        conn.commit()
        dataset_id = cursor.lastrowid
        print(f"Dataset '{name}' added with ID: {dataset_id}")
        return dataset_id
    except sqlite3.IntegrityError:
        print(f"Dataset name '{name}' already exists.")
        return None
    except sqlite3.Error as e:
        print(f"Error adding dataset '{name}': {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def add_card(
    dataset_id,
    question,
    correct_answer,
    choice1,
    choice2,
    choice3,
    choice4,
    choice5=None,
    notes="",
):
    """Adds a new card to a specific dataset, including optional notes. mark_for_review defaults to False."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Explicitly list columns, rely on DB default for mark_for_review
        cursor.execute(
            """
            INSERT INTO cards (dataset_id, question, correct_answer, choice1, choice2, choice3, choice4, choice5, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                dataset_id,
                question,
                correct_answer,
                choice1,
                choice2,
                choice3,
                choice4,
                choice5,
                notes,
            ),
        )
        conn.commit()
        # print(f"Card added to dataset {dataset_id}: {question[:30]}...") # Optional logging
        return True
    except sqlite3.Error as e:
        print(f"Error adding card to dataset {dataset_id}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_datasets():
    """Retrieves all datasets from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name FROM datasets ORDER BY name")
        datasets = cursor.fetchall()
        return datasets
    except sqlite3.Error as e:
        print(f"Error fetching datasets: {e}")
        return []
    finally:
        conn.close()


def get_cards_by_dataset(dataset_id):
    """
    Retrieves all cards for a specific dataset, ordered by ID.
    Includes the 'notes' and 'mark_for_review' fields.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # SELECT * will include the new columns
        cursor.execute(
            "SELECT * FROM cards WHERE dataset_id = ? ORDER BY id", (dataset_id,)
        )
        cards = cursor.fetchall()
        return cards
    except sqlite3.Error as e:
        print(f"Error fetching cards for dataset {dataset_id}: {e}")
        return []
    finally:
        conn.close()


def get_review_cards_by_dataset(dataset_id):
    """
    Retrieves cards marked for review for a specific dataset, ordered by ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Filter by mark_for_review = 1 (TRUE)
        cursor.execute(
            "SELECT * FROM cards WHERE dataset_id = ? AND mark_for_review = 1 ORDER BY id",
            (dataset_id,),
        )
        cards = cursor.fetchall()
        return cards
    except sqlite3.Error as e:
        print(f"Error fetching review cards for dataset {dataset_id}: {e}")
        return []
    finally:
        conn.close()


def get_dataset_id_by_name(name):
    """Retrieves the ID of a dataset by its name. Returns ID or None if not found."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM datasets WHERE name = ?", (name,))
        result = cursor.fetchone()
        return result["id"] if result else None
    except sqlite3.Error as e:
        print(f"Error fetching dataset ID for name '{name}': {e}")
        return None
    finally:
        conn.close()


def delete_dataset(dataset_id):
    """Deletes a dataset and all its associated cards (due to ON DELETE CASCADE)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Dataset {dataset_id} deleted successfully.")
            return True
        else:
            print(f"Dataset {dataset_id} not found for deletion.")
            return False  # Indicate dataset wasn't found
    except sqlite3.Error as e:
        print(f"Error deleting dataset {dataset_id}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def update_card_notes(card_id, notes):
    """Updates the notes for a specific card."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE cards SET notes = ? WHERE id = ?", (notes, card_id))
        conn.commit()
        if cursor.rowcount > 0:
            # print(f"Notes updated for card {card_id}.") # Optional logging
            return True
        else:
            print(f"Card {card_id} not found for notes update.")
            return False  # Indicate card wasn't found
    except sqlite3.Error as e:
        print(f"Error updating notes for card {card_id}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def toggle_card_review_status(card_id):
    """Toggles the mark_for_review status for a specific card."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Toggle the boolean value (0 becomes 1, 1 becomes 0)
        cursor.execute(
            "UPDATE cards SET mark_for_review = NOT mark_for_review WHERE id = ?",
            (card_id,),
        )
        conn.commit()
        if cursor.rowcount > 0:
            # Optionally, fetch the new status to return it? For now, just success/fail.
            # cursor.execute("SELECT mark_for_review FROM cards WHERE id = ?", (card_id,))
            # new_status = cursor.fetchone()['mark_for_review']
            # print(f"Review status toggled for card {card_id}. New status: {new_status}")
            return True
        else:
            print(f"Card {card_id} not found for review status toggle.")
            return False  # Indicate card wasn't found
    except sqlite3.Error as e:
        print(f"Error toggling review status for card {card_id}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    # Example usage: Initialize DB if script is run directly
    print("Initializing database directly...")
    init_db()
    # You could add test data insertion here if needed
    # ds_id = add_dataset("Sample Set with Notes")
    # if ds_id:
    #     add_card(ds_id, "Q1?", "A1", "C1", "C2", "C3", "C4", notes="This is a note for Q1.")
    #     add_card(ds_id, "Q2?", "A2", "C1", "C2", "C3", "C4")
    #     update_card_notes(1, "Updated note for card 1") # Assuming card ID 1 exists
    #     toggle_card_review_status(1) # Example toggle
    #     delete_dataset(ds_id) # Example deletion
