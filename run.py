from app import app, get_db
import os
import sqlite3

# This script is for local development and deployment.
# It initializes the database only if it doesn't exist.

def init_db():
    """Initializes the database by executing the schema.sql script."""
    # Use a regular connection to avoid Flask's g object
    db = sqlite3.connect(app.config['LOCAL_DATABASE'])
    with open('schema.sql', 'r') as f:
        db.executescript(f.read())
    db.commit()
    db.close()
    print("Local SQLite database initialized successfully.")

if __name__ == '__main__':
    # Check for local SQLite database existence only if DATABASE_URL is not set
    if not os.environ.get('DATABASE_URL') and not os.path.exists(app.config['LOCAL_DATABASE']):
        print("Local database not found. Initializing new SQLite database...")
        init_db()
    
    app.run(debug=True)
