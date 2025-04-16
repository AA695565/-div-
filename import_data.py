import csv
import sqlite3
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.join(BASE_DIR, 'data', 'students.csv')
DB_FILE_PATH = os.path.join(BASE_DIR, 'data', 'students.db')
TABLE_NAME = 'students'

def import_csv_to_db():
    """Imports data from the CSV file into the SQLite database."""
    print(f"Starting import from {CSV_FILE_PATH} to {DB_FILE_PATH}...")

    # Check if CSV file exists
    if not os.path.exists(CSV_FILE_PATH):
        print(f"Error: CSV file not found at {CSV_FILE_PATH}")
        print("Please place your 'students.csv' file in the 'data' directory.")
        return

    # Delete existing database file if it exists to ensure fresh import
    if os.path.exists(DB_FILE_PATH):
        print(f"Removing existing database file: {DB_FILE_PATH}")
        os.remove(DB_FILE_PATH)

    conn = None # Initialize conn to None
    try:
        # Connect to SQLite database (creates the file if it doesn't exist)
        conn = sqlite3.connect(DB_FILE_PATH)
        cursor = conn.cursor()

        # Create the table
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            registration_number TEXT,
            student_name TEXT,
            total_marks INTEGER
        )
        ''')
        print(f"Table '{TABLE_NAME}' created successfully (if it didn't exist).")

        # Read the CSV file and insert data
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader) # Skip header row

            print(f"Importing rows from {CSV_FILE_PATH}...")
            rows_imported = 0
            for row in csv_reader:
                if len(row) == 3: # Ensure row has expected number of columns
                    cursor.execute(f'''
                    INSERT INTO {TABLE_NAME} (registration_number, student_name, total_marks)
                    VALUES (?, ?, ?)
                    ''', (row[0], row[1], row[2]))
                    rows_imported += 1
                else:
                    print(f"Skipping malformed row: {row}")

            print(f"Successfully imported {rows_imported} rows.")

        # Create indexes for faster searching (optional but recommended)
        print("Creating indexes...")
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_reg_num ON {TABLE_NAME} (registration_number)')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_name ON {TABLE_NAME} (student_name)')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_marks ON {TABLE_NAME} (total_marks)')
        print("Indexes created successfully.")

        # Commit changes
        conn.commit()
        print("Database changes committed.")

    except sqlite3.Error as e:
        print(f"SQLite error during import: {e}")
    except FileNotFoundError:
         print(f"Error: Could not find the CSV file at {CSV_FILE_PATH}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    import_csv_to_db() 