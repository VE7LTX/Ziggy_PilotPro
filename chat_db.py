"""
Title: Chat Database Management (PilotPro)
File Name: chat_db.py
Description:
This module manages the SQLite database operations for the PilotPro chat application. It provides functionalities to 
manage chat sessions, store messages, retrieve messages, and handle encryption of chat messages.

Author: Matthew Schafer
Date: September 2, 2023
Company: VE7LTX Diagonal Thinking LTD

Requirements:
- Python 3.x
- Required packages: sqlite3, os, logging, typing
- SQLite database named 'chat.db' (default) inside the 'DB' folder.

Module Logic Breakdown:
- Encryption (`encrypt` and `decrypt`) functions to handle chat message security.
- `ChatDatabase` Class:
  - Manages the SQLite database connection.
  - Provides functionalities to open, close, and manage database connections.
  - Provides methods to insert, retrieve and manage chat messages.
  - Uses context management to handle the database connection.
  - Error handling for SQLite operations and general exceptions.

Usage:
1. Ensure the required packages are installed using 'pip install [package name]'.
2. Instantiate the ChatDatabase class and use its methods to manage chat sessions.
3. Close the database connection after usage.

Header Comment Explanation:
- This module focuses on database operations for the PilotPro chat application.
- SQLite is used as the database. Messages are encrypted before storage for security.
- Developers can use the provided functionalities to manage chat sessions, store messages, and retrieve them.
- Comprehensive logging is implemented for debugging purposes.

Debugging Note:
- This module has been thoroughly debugged and provides granular error logs when operating in DEBUG mode. This ensures that developers can trace issues back to their source and understand the sequence of operations leading up to any errors.

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
        logging.debug(f"CLASS ChatDatabase - __init__: Initializing ChatDatabase with database name: {db_name}")
        
        # Ensure the DB folder exists or create it
        if not os.path.exists(self.db_folder):
            os.makedirs(self.db_folder)
            logging.debug(f"CLASS ChatDatabase - __init__: Created database directory: {self.db_folder}")
        else:
            logging.debug(f"CLASS ChatDatabase - __init__: Database directory {self.db_folder} already exists.")
        
        self.db_name = os.path.join(self.db_folder, db_name)
        self.conn = None
        logging.info(f"CLASS ChatDatabase - __init__: ChatDatabase initialized successfully with database path: {self.db_name}")

    def __enter__(self):
        logging.debug(f"CLASS ChatDatabase - __enter__: Entering context management for database: {self.db_name}")
        self.open_connection()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logging.debug(f"CLASS ChatDatabase - __exit__: Exiting context management for database: {self.db_name}")
        if exc_type or exc_value or traceback:
            logging.error(f"CLASS ChatDatabase - __exit__: Exception detected during context management. Type: {exc_type}, Value: {exc_value}.")
        self.close_connection()

    def open_connection(self):
        logging.debug(f"CLASS ChatDatabase - open_connection: Preparing to open connection to database: {self.db_name}")
        
        if not self.conn:
            try:
                self.conn = sqlite3.connect(self.db_name)
                logging.debug(f"CLASS ChatDatabase - open_connection: Successfully established connection to database: {self.db_name}")
                
                self._create_tables()
                logging.debug(f"CLASS ChatDatabase - open_connection: Tables checked/created successfully in database: {self.db_name}")
            except sqlite3.OperationalError as oe:
                logging.error(f"CLASS ChatDatabase - open_connection: Operational Error: {oe}")
            except sqlite3.Error as e:
                logging.error(f"CLASS ChatDatabase - open_connection: sqlite3 Error: {e}")
            except Exception as e:
                logging.exception(f"CLASS ChatDatabase - open_connection: Unexpected Error: {e}")
        else:
            logging.warning(f"CLASS ChatDatabase - open_connection: Connection already active to database: {self.db_name}")


    def close_connection(self):
        """Close the database connection."""
        logging.debug(f"CLASS ChatDatabase - close_connection: Preparing to close connection to database: {self.db_name}")
        
        if self.conn:
            try:
                self.conn.close()
                logging.debug(f"CLASS ChatDatabase - close_connection: Connection closed successfully for database: {self.db_name}")
            except sqlite3.OperationalError as oe:
                logging.error(f"CLASS ChatDatabase - close_connection: Operational Error while closing: {oe}")
            except sqlite3.Error as e:
                logging.error(f"CLASS ChatDatabase - close_connection: sqlite3 Error while closing: {e}")
            except Exception as e:
                logging.exception(f"CLASS ChatDatabase - close_connection: Unexpected Error while closing: {e}")
            finally:
                self.conn = None
                logging.debug(f"CLASS ChatDatabase - close_connection: Connection variable reset to None.")
        else:
            logging.warning(f"CLASS ChatDatabase - close_connection: Connection is already closed or was never initialized for database: {self.db_name}")


    def _create_tables(self):
        """
        Create tables if they don't exist.
        """
        # Starting the table creation/checking process
        logging.debug("CLASS ChatDatabase - _create_tables: Attempting to create/check tables.")

        try:
            # Using a context manager for the database connection
            with self.conn:
                # SQL statement to create the table if it doesn't exist
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS chat_sessions (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        message TEXT NOT NULL,
                        role TEXT NOT NULL,
                        encrypted BOOLEAN DEFAULT FALSE
                    )
                """)
            # Successful table creation/checking
            logging.debug("CLASS ChatDatabase - _create_tables: Tables created/checked successfully.")

        # Handling any SQLite errors during the process
        except sqlite3.Error as e:
            # Logging the error along with the traceback
            logging.exception(f"CLASS ChatDatabase - _create_tables: Error creating/checking table.")  # Exception logs the traceback


    def insert_message(self, username: str, message: str, role: str, encrypt_message: bool = True) -> None:
        """
        Inserts a new message into the chat_sessions table in the database.

        Parameters:
        - username (str): The name of the user.
        - message (str): The content of the message.
        - role (str): Role of the user (e.g., 'user', 'assistant').
        - encrypt_message (bool, optional): Flag to determine if the message should be encrypted before storage. Default is True.

        Returns:
        - None
        """
        logging.debug(f"CLASS ChatDatabase - insert_message: Preparing to insert message for user: {username}. Message: {message}")

        try:
            encrypted = False
            if encrypt_message:
                message = encrypt(message)
                encrypted = True
                logging.debug(f"CLASS ChatDatabase - insert_message: Message encrypted successfully for user: {username}")

            with self.conn:
                self.conn.execute("INSERT INTO chat_sessions (username, message, role, encrypted) VALUES (?, ?, ?, ?)",
                                (username, message, role, encrypted))
            logging.debug(f"CLASS ChatDatabase - insert_message: Message inserted successfully into the database for user: {username}")

        except sqlite3.Error as e:
            logging.exception(f"CLASS ChatDatabase - insert_message: Database error occurred while inserting message for user: {username}. Error: {e}")
        except Exception as e:
            logging.exception(f"CLASS ChatDatabase - insert_message: An unexpected error occurred while inserting message for user: {username}. Error: {e}")


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
        """Retrieve the last 'n' messages for a given user."""
        
        # Logging the start of the method with input details.
        logging.debug("CLASS ChatDatabase - get_last_n_messages: Starting method. User: %s, Retrieving last %s messages.", username, n)
        
        # Check if the connection is not open and log the error with the database name.
        if not self.conn:
            logging.error("CLASS ChatDatabase - get_last_n_messages: Connection is not open. Database: %s.", self.db_name)
            logging.error("Recommendation: Ensure the database connection is initialized and accessible.")
            return []
        
        try:
            with self.conn:
                # Execute the SQL query.
                cursor = self.conn.execute(
                    "SELECT message, role, encrypted FROM chat_sessions WHERE username = ? "
                    "ORDER BY id DESC LIMIT ?", (username, n))
                messages = cursor.fetchall()
                
                # Log a warning if no messages are found for the given user.
                if not messages:
                    logging.warning("CLASS ChatDatabase - get_last_n_messages: No messages found for user %s.", username)
                
                # Decrypt the messages if they are encrypted.
                decrypted_messages = [(decrypt(message) if encrypted else message, role) for message, role, encrypted in messages]
                
                # Log the decrypted messages retrieved for the user.
                logging.debug("CLASS ChatDatabase - get_last_n_messages: Messages retrieved for user %s: %s", username, decrypted_messages)
                
                return decrypted_messages
            
        except sqlite3.Error as e:
            # Log detailed error information if there's an exception while retrieving messages.
            logging.error("CLASS ChatDatabase - get_last_n_messages: Error retrieving messages for user %s from database %s.", username, self.db_name)
            logging.error("Exception Type: %s.", type(e).__name__)
            logging.error("Exception Args: %s.", e.args)
            logging.error("Recommendation: Check the structure of the 'chat_sessions' table and ensure it matches the query.")
            
            return []
        
        finally:
            # Log the completion of method execution.
            logging.info("CLASS ChatDatabase - get_last_n_messages: Method execution complete for user %s.", username)


    def close(self):
        """Close the database connection."""
        logging.debug(f"CLASS ChatDatabase - close: Initiating the closing procedure for database: {self.db_name}.")
        
        # Check if the connection is active before attempting to close
        if self.conn:
            logging.debug(f"CLASS ChatDatabase - close: Connection is active. Proceeding to close the connection to database: {self.db_name}.")
            self.close_connection()
            logging.debug(f"CLASS ChatDatabase - close: Close connection procedure completed for database: {self.db_name}.")
        else:
            logging.debug(f"CLASS ChatDatabase - close: Connection is already closed or was never opened for database: {self.db_name}. Skipping close procedure.")


# Ensure logging is configured for debugging
logging.basicConfig(level=logging.DEBUG)

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# End of Chat Database Management (PilotPro) Module.

# Module Footnotes:

# Database Structure:
# The primary database this module interacts with is 'chat.db'. The 'chat_sessions' table within this database
# is structured to contain columns for unique IDs, usernames, messages, roles, and encryption status.

# Security Measures:
# The module employs basic encryption for chat messages. For enhanced security, consider integrating with more
# advanced encryption libraries or methods.

# Performance Considerations:
# This module has been optimized for small to medium-sized chat applications. For large-scale applications or
# significant concurrent user loads, consider employing a more scalable database system and optimizing database operations.

# Dependencies:
# Ensure that all required packages mentioned in the header are installed and compatible with the Python version used.

# Future Enhancements:
# 1. Integration with more advanced encryption libraries for enhanced security.
# 2. Adding database indexing to improve retrieval speeds.
# 3. Implementing a backup mechanism for the database.

# Test Cases:
# Ensure to have a suite of test cases to validate the module's functionalities. Test for scenarios including:
# - Normal operation (e.g., message insertion, retrieval)
# - Edge cases (e.g., empty messages, very long messages)
# - Error scenarios (e.g., database disconnects, encryption errors)

# Feedback and Contributions:
# Feedback is always welcome. For contributions, bug reports, or feature requests, please reach out to the author.
# Ensure to follow the coding standards and guidelines mentioned in the header when contributing.

# Disclaimer:
# This module is provided as-is. While every effort has been made to ensure reliability and security, the author and
# VE7LTX Diagonal Thinking LTD take no responsibility for any issues or damages that may arise from its use.

# Last Updated: August 31, 2023

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
