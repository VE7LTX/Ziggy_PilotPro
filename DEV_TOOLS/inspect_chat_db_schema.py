import sqlite3

# Connect to the SQLite database again
conn = sqlite3.connect('./DB/chat.db')
cursor = conn.cursor()

# Get the list of tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Get schema for each table
schemas = {}
for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name})")
    schemas[table_name] = cursor.fetchall()

schemas
print(schemas)