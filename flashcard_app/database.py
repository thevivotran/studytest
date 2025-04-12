import sqlite3
import os

# Define the path for the database file within the persistent volume
DATABASE_DIR = '/data'
DATABASE_PATH = os.path.join(DATABASE_DIR, 'flashcard.db')

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    # Ensure the /data directory exists (important for the first run)
    # Although the volume mount should handle this, a check doesn't hurt.
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    # Return rows as dictionary-like objects
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database by creating tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Create datasets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')

        # Create cards table
        cursor.execute('''
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
        ''')
        conn.commit()
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
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
        return None
    finally:
        conn.close()

def add_card(dataset_id, question, correct_answer, choice1, choice2, choice3, choice4, choice5=None):
    """Adds a new card to a specific dataset."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO cards (dataset_id, question, correct_answer, choice1, choice2, choice3, choice4, choice5)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (dataset_id, question, correct_answer, choice1, choice2, choice3, choice4, choice5))
        conn.commit()
        # print(f"Card added to dataset {dataset_id}: {question[:30]}...") # Optional logging
        return True
    except sqlite3.Error as e:
        print(f"Error adding card to dataset {dataset_id}: {e}")
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
    """Retrieves all cards for a specific dataset, ordered by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM cards WHERE dataset_id = ? ORDER BY id", (dataset_id,))
        cards = cursor.fetchall()
        return cards
    except sqlite3.Error as e:
        print(f"Error fetching cards for dataset {dataset_id}: {e}")
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
        return result['id'] if result else None
    except sqlite3.Error as e:
        print(f"Error fetching dataset ID for name '{name}': {e}")
        return None
    finally:
        conn.close()

if __name__ == '__main__':
    # Example usage: Initialize DB if script is run directly
    print("Initializing database directly...")
    init_db()
    # You could add test data insertion here if needed
    # add_dataset("Sample Set")
    # add_card(1, "Q1?", "A1", "C1", "C2", "C3", "C4")