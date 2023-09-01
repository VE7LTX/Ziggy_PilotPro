"""
Title: Chat Database Management (PilotPro)
File Name: chat_db.py
Description: 
This module manages the SQLite database operations for the PilotPro chat application. It provides functionalities to manage chat sessions, store messages, and retrieve messages. Data encryption is used for message storage.

Author: Matthew Schafer
Date: August 31, 2023
Company: VE7LTX Diagonal Thinking LTD

Requirements:
- Python 3.x
- Required packages: sqlite3, os, logging, typing
- SQLite database named 'chat.db' (default) inside the 'DB' folder.

Module Logic Breakdown:
- Encryption and decryption functions for chat messages.
- `ChatDatabase` Class:
  - Manages the SQLite database connection.
  - Provides functionalities to open, close, and manage database connections.
  - Allows for the creation of necessary tables.
  - Offers methods to insert and retrieve chat messages.
  - Uses context management to handle the database connection.

Usage:
1. Ensure the required packages are installed using 'pip install [package name]'.
2. Instantiate the ChatDatabase class and use its methods to manage chat sessions.
3. Close the database connection after usage.

Header Comment Explanation:
- This module focuses on database operations for the PilotPro chat application.
- SQLite is used as the database, and messages are encrypted before storage.
- Developers can use the provided functionalities to manage chat sessions, store messages, and retrieve them.
- Best practices for production use include data validation and further security enhancements.

Note: Developers should be cautious about using simple encryption methods. For production use, consider more secure encryption libraries and practices.
"""
import os
import sqlite3
from typing import List, Tuple
import logging

def encrypt(message: str) -> str:
    return ''.join(chr(ord(c) + 3) for c in message)

def decrypt(encrypted_message: str) -> str:
    return ''.join(chr(ord(c) - 3) for c in encrypted_message)

class ChatDatabase:
    def __init__(self, db_name: str = "chat.db"):
        self.db_folder = "DB"  # Default folder name
        # Ensure the DB folder exists or create it
        if not os.path.exists(self.db_folder):
            os.makedirs(self.db_folder)
        self.db_name = os.path.join(self.db_folder, db_name)
        self.conn = None

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_connection()

    def open_connection(self):
        if not self.conn:
            try:
                self.conn = sqlite3.connect(self.db_name)
                self._create_tables()
                logging.debug("CLASS ChatDatabase DEBUG open_connection(self): Connection opened successfully")
            except sqlite3.Error as e:
                logging.error(f"CLASS ChatDatabase DEBUG open_connection(self): Error opening connection: {e}")
                self.conn = None
        else:
            logging.warning("CLASS ChatDatabase DEBUG open_connection(self): Connection is already open!")

    def close_connection(self):
        if self.conn:
            self.conn.close()
            self.conn = None
        else:
            logging.warning("CLASS ChatDatabase DEBUG close_connection Connection is already closed!")

    def _create_tables(self):
        """Create tables if they don't exist."""
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS chat_sessions (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        message TEXT NOT NULL,
                        role TEXT NOT NULL,
                        encrypted BOOLEAN DEFAULT FALSE
                    )
                """)
        except sqlite3.Error as e:
            logging.error(f"CLASS ChatDatabase DEBUG _create_tables Error creating table: {e}")

    def insert_message(self, username: str, message: str, role: str, encrypt_message: bool = True) -> None:
        """Insert a new message into the database."""
        try:
            encrypted = False
            if encrypt_message:
                message = encrypt(message)
                encrypted = True

            with self.conn:
                self.conn.execute("INSERT INTO chat_sessions (username, message, role, encrypted) VALUES (?, ?, ?, ?)",
                                (username, message, role, encrypted))
        except sqlite3.Error as e:
            logging.error(f"CLASS ChatDatabase DEBUG insert_message Error inserting message: {e}")

    def get_messages(self, username: str) -> List[Tuple[str, str, str]]:
        """Retrieve all messages for a given username."""
        if not self.conn:
            logging.error("CLASS ChatDatabase DEBUG get_messages Connection is not open!")
            return []
        try:
            with self.conn:
                cursor = self.conn.execute("SELECT message, role, encrypted FROM chat_sessions WHERE username = ?", (username,))
                messages = cursor.fetchall()
                return [(decrypt(message) if encrypted else message, role) for message, role, encrypted in messages]
        except sqlite3.Error as e:
            logging.error(f"CLASS ChatDatabase DEBUG get_messages Error retrieving messages: {e}")
            return []

    def get_last_n_messages(self, n: int, username: str) -> List[Tuple[str, str]]:
        if not self.conn:
            logging.error("CLASS ChatDatabase DEBUG get_last_n_messages Connection is not open!")
            return []
        try:
            with self.conn:
                cursor = self.conn.execute("""
                    SELECT message, role, encrypted FROM chat_sessions WHERE username = ? 
                    ORDER BY id DESC LIMIT ?
                """, (username, n))
                messages = cursor.fetchall()
                return [(decrypt(message) if encrypted else message, role) for message, role, encrypted in messages]
        except sqlite3.Error as e:
            logging.error(f"\nCLASS ChatDatabase DEBUG get_last_n_messages Error retrieving messages: {e}")
            return []

    def close(self):
        """Close the database connection."""
        self.close_connection()

# Ensure logging is configured for debugging
logging.basicConfig(level=logging.INFO)

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# End of Chat Database Management (PilotPro) Module.
#
# Summary:
# - This module provides a comprehensive interface to manage chat sessions in the SQLite database for the PilotPro application.
# - It incorporates simple encryption methods for message storage and retrieval. 
# - The `ChatDatabase` class serves as the primary interface for database operations.
#
# Key Features:
# 1. Context management for efficient database connection handling.
# 2. Encryption and decryption of chat messages.
# 3. CRUD operations for chat sessions in the SQLite database.
# 4. Logging capabilities to monitor and debug operations.
#
# Future Considerations:
# - Enhance encryption methods for better security in production environments.
# - Introduce additional error handling and recovery mechanisms.
# - Expand database schema to cater to evolving application needs.
#
# Remember to close the database connection after performing operations to ensure data integrity and release resources.
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

