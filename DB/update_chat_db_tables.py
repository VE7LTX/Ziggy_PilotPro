import sqlite3
import os
import shutil

def backup_database(original_path: str, backup_dir: str):
    """Backup the database to the specified backup directory."""
    # Ensure the backup directory exists, if not, create it
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Define the backup path based on the original filename and the backup directory
    backup_path = os.path.join(backup_dir, os.path.basename(original_path))
    
    # Copy the original database to the backup directory
    shutil.copy2(original_path, backup_path)

def create_messages_table_in_local_db(db_path: str):
    """Create the messages table in the local SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Define the schema for the messages table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    cursor.execute(create_table_sql)
    conn.commit()
    cursor.close()
    conn.close()

# Paths
# Paths
db_path = r"DB\chat.db"
backup_dir = r".\backup"


# Backup and update the database
backup_database(db_path, backup_dir)
create_messages_table_in_local_db(db_path)

print(f"Backed up the database to {backup_dir}")
print("Updated the local database successfully!")
