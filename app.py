import os
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE_PATH = os.path.join(BASE_DIR, 'data', 'students.db')
TABLE_NAME = 'students'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE_PATH)
        conn.row_factory = sqlite3.Row # Return rows as dictionary-like objects
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        # Consider logging this error
    return conn

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/search')
def search():
    """Handles search requests based on specific fields and returns results as JSON."""
    query = request.args.get('q', '')
    field = request.args.get('field', '') # Get the field to search
    results = []

    # Basic validation
    valid_fields = ['registration_number', 'student_name', 'total_marks']
    if not query or field not in valid_fields:
        print(f"Invalid search request: field='{field}', query='{query}'")
        return jsonify({"error": "Invalid search field or query"}), 400 # Bad request

    conn = get_db_connection()
    if not conn:
        print("Database connection failed")
        return jsonify({"error": "Database connection error"}), 500 # Internal server error

    cursor = conn.cursor()
    sql = f"SELECT registration_number, student_name, total_marks FROM {TABLE_NAME}"
    params = []

    try:
        if field == 'registration_number':
            sql += " WHERE LOWER(registration_number) LIKE LOWER(?)"
            params.append(f'%{query}%')
        elif field == 'student_name':
            sql += " WHERE LOWER(student_name) LIKE LOWER(?)"
            params.append(f'%{query}%')
        elif field == 'total_marks':
            # Validate that the query is an integer for exact match
            try:
                marks_query = int(query)
                sql += " WHERE total_marks = ?"
                params.append(marks_query)
            except ValueError:
                print(f"Invalid non-integer query for total_marks: '{query}'")
                # Return empty results if marks query is not a number
                conn.close()
                return jsonify([])

        sql += " ORDER BY student_name LIMIT 100" # Add ordering and limit

        print(f"Executing SQL: {sql} with params: {params}") # Debugging log
        cursor.execute(sql, tuple(params))
        results = [dict(row) for row in cursor.fetchall()]

    except sqlite3.Error as e:
        print(f"Error during search query execution: {e}")
        print(f"SQL attempted: {sql}")
        print(f"Params: {params}")
        return jsonify({"error": "Error executing search query"}), 500
    finally:
        conn.close()

    return jsonify(results)

if __name__ == '__main__':
    # Check if database exists before starting
    if not os.path.exists(DB_FILE_PATH):
        print("Error: Database file not found!")
        print(f"Please run 'python import_data.py' first to create and populate the database at {DB_FILE_PATH}")
    else:
        print(f"Database found at {DB_FILE_PATH}")
        print("Starting Flask server...")
        # Use debug=True for development, remove or set to False for production
        app.run(debug=True) 