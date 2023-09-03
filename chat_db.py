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
    """
    Encrypts the given message by adding 3 to the ordinal value of each character.

    Parameters:
    - message (str): The plain text message to be encrypted.

    Returns:
    - str: The encrypted message.
    """
    logging.debug("Function encrypt - Start: Beginning encryption process.")
    
    # Logging input message length and first few characters for context without revealing entire content
    logging.debug(f"Function encrypt - Input: Processing message of length {len(message)}. Starting characters: {message[:10]}...")

    encrypted_message = ""
    try:
        for c in message:
            encrypted_char = chr(ord(c) + 3)
            encrypted_message += encrypted_char

        logging.debug(f"Function encrypt - Success: Message successfully encrypted. Starting characters of encrypted message: {encrypted_message[:10]}...")
        return encrypted_message
    except Exception as e:
        logging.error(f"Function encrypt - Error: Failed to encrypt character '{c}' from message: {message[:10]}... Error: {e}")
        logging.exception(f"Function encrypt - Exception: Complete traceback for the error during encryption.")
        raise

def decrypt(encrypted_message: str) -> str:
    """
    Decrypts the given encrypted message by subtracting 3 from the ordinal value of each character.

    Parameters:
    - encrypted_message (str): The encrypted message to be decrypted.

    Returns:
    - str: The decrypted message.
    """
    logging.debug("Function decrypt - Start: Preparing to decrypt the encrypted message.")
    
    # Validating the input
    if not encrypted_message or not isinstance(encrypted_message, str):
        logging.warning(f"Function decrypt - Warning: Invalid encrypted message provided: {encrypted_message}. Expected a non-empty string.")
        return ""
    
    try:
        logging.debug(f"Function decrypt - Process: Starting decryption for encrypted message: {encrypted_message}.")
        decrypted_chars = []  # List to hold decrypted characters for better debugging
        
        for c in encrypted_message:
            decrypted_char = chr(ord(c) - 3)
            decrypted_chars.append(decrypted_char)

        decrypted_message = ''.join(decrypted_chars)
        logging.debug(f"Function decrypt - Success: Message successfully decrypted. Encrypted: {encrypted_message}, Decrypted: {decrypted_message}")
        return decrypted_message

    except Exception as e:
        logging.exception(f"Function decrypt - Error: An error occurred during decryption for encrypted message: {encrypted_message}. Error: {e}")
        raise


class ChatDatabaseError(Exception):
    """Base exception class for ChatDatabase related errors."""
    pass
    
    
class ChatDatabase:
    def __init__(self, db_name: str = "chat.db"):
        logging.debug(f"CLASS ChatDatabase - __init__: Method entry. Initializing ChatDatabase.")
        
        self.db_folder = "DB"
        logging.debug(f"CLASS ChatDatabase - __init__: Setting default database folder to: {self.db_folder}")

        # Ensure the DB folder exists or create it
        if not os.path.exists(self.db_folder):
            os.makedirs(self.db_folder)
            logging.debug(f"CLASS ChatDatabase - __init__: Successfully created database directory: {self.db_folder}")

        self.db_name = os.path.join(self.db_folder, db_name)
        self.conn = None

    def __enter__(self):
        try:
            self.open_connection()
        except ChatDatabaseError as e:
            logging.error(f"CLASS ChatDatabase - __enter__: {e}")
            # Handle the error as you see fit, e.g., by raising another exception or exiting the program.
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_connection()

    def is_connection_valid(self) -> bool:
        """
        Checks if the current database connection is valid.

        Returns:
        - True if the connection is valid, False otherwise.
        """
        # If connection is None, it is not valid
        if self.conn is None:
            return False
        
        try:
            self.conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False

    def open_connection(self):
        """
        Opens a connection to the database and creates tables if they do not exist.
        """
        # Check if the database file exists
        if not os.path.exists(self.db_name):
            logging.warning(f"CLASS ChatDatabase - open_connection: Database file {self.db_name} does not exist. Will be created upon connection.")

        # Attempt to connect to the database
        try:
            self.conn = sqlite3.connect(self.db_name)
            self._create_tables()
        except sqlite3.Error as e:
            logging.error(f"CLASS ChatDatabase - open_connection: sqlite3 Error occurred: {e}")
            raise ChatDatabaseError("Failed to connect to the database.")

        # Check if the connection was created successfully
        if self.conn is None:
            logging.error("Failed to create the database connection.")
            raise ChatDatabaseError("Failed to create the database connection.")
        else:
            logging.warning(f"CLASS ChatDatabase - open_connection: Connection already active.")

    def close_connection(self):
        """
        Closes the connection to the database.
        """
        # Check if the connection is valid before attempting to close it
        if self.is_connection_valid():
            try:
                self.conn.close()
            except sqlite3.Error as e:
                logging.error(f"CLASS ChatDatabase - close_connection: sqlite3 Error occurred: {e}")
                raise ChatDatabaseError("Failed to close the database connection.")
            finally:
                # Ensure the connection is set to None, even if an error occurs
                self.conn = None


    def _create_tables(self):
        """
        Creates the necessary tables in the database.
        """
        if not self.is_connection_valid():
            raise ChatDatabaseError("No active database connection.")

        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS chat_sessions (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        message TEXT NOT NULL,
                        role TEXT NOT NULL,
                        encrypted BOOLEAN DEFAULT FALSE,
                        response TEXT,
                        response_encrypted BOOLEAN DEFAULT FALSE
                    )
                """)
        except sqlite3.Error as e:
            logging.error(f"CLASS ChatDatabase - _create_tables: sqlite3 Error occurred: {e}")
            raise ChatDatabaseError("Failed to create or validate tables.")

    def save_message(self, username: str, message: str, role: str) -> int:
        """
        Saves a message into the database.

        Parameters:
        - username (str): The name of the user.
        - message (str): The content of the message.
        - role (str): Role of the user (e.g., 'user', 'assistant').

        Returns:
        - The row id of the inserted message.
        """
        try:
            if not self.is_connection_valid():
                self.open_connection()
                if not self.is_connection_valid():
                    logging.error("save_message: No active connection to the database")
                    raise ChatDatabaseError("No active connection to the database.")

            insert_query = "INSERT INTO chat_sessions (username, message, role) VALUES (?, ?, ?)"
            cursor = self.conn.cursor()
            cursor.execute(insert_query, (username, message, role))
            self.conn.commit()
            return cursor.lastrowid

        except sqlite3.Error as e:
            logging.error(f"save_message: sqlite3 Error occurred: {e}")
            raise ChatDatabaseError(f"Error saving message. SQLite Error: {e}")

        except Exception as e:
            logging.exception(f"save_message: Unexpected Error occurred: {e}")
            raise ChatDatabaseError(f"Unexpected error occurred: {e}")

    def insert_message(self, username: str, message: str, role: str, response: str, encrypt_message: bool = True) -> None:
        """
        Inserts a new message and the corresponding AI response into the chat_sessions table in the database.
        
        Parameters:
        - username (str): The name of the user.
        - message (str): The content of the message.
        - role (str): Role of the user (e.g., 'user', 'assistant').
        - response (str): The AI's response to the message.
        - encrypt_message (bool, optional): Flag to determine if the message and response should be encrypted before storage. Default is True.

        Returns:
        - None
        """
        logging.debug(f"CLASS ChatDatabase - insert_message: Entry. Initiating message insertion for user: {username}.")
        
        # Checking for database connection status
        if not self.is_connection_valid():
            logging.error(f"CLASS ChatDatabase - insert_message: No active connection to database: {self.db_name}. Ensure the connection is established before inserting messages.")
            return

        try:
            encrypted = False
            encrypted_response = False

            if encrypt_message:
                logging.debug(f"CLASS ChatDatabase - insert_message: Encrypting message for user: {username}.")
                message = encrypt(message)
                response = encrypt(response)
                encrypted = True
                encrypted_response = True
                logging.debug(f"CLASS ChatDatabase - insert_message: Message and response encrypted successfully for user: {username}.")

            logging.debug(f"CLASS ChatDatabase - insert_message: Preparing SQL query for insertion into the 'chat_sessions' table.")
            
            with self.conn:
                logging.debug(f"CLASS ChatDatabase - insert_message: Beginning transaction for inserting message.")
                self.conn.execute(
                    "INSERT INTO chat_sessions (username, message, role, encrypted, response, response_encrypted) VALUES (?, ?, ?, ?, ?, ?)",
                    (username, message, role, encrypted, response, encrypted_response)
                )
                logging.debug(f"CLASS ChatDatabase - insert_message: Message and response inserted successfully into the database for user: {username}.")

        except sqlite3.Error as e:
            logging.exception(f"CLASS ChatDatabase - insert_message: sqlite3 error occurred for user: {username}. Error: {e}.")
        except Exception as e:
            logging.exception(f"CLASS ChatDatabase - insert_message: Unexpected error for user: {username}. Error: {e}.")

        logging.debug(f"CLASS ChatDatabase - insert_message: Exit. Completed message insertion process for user: {username}.")

    def get_messages(self, username: str) -> List[Tuple[str, str, str, str]]:
        """
        Retrieve all messages and responses for a given username.

        Returns:
        - List of tuples containing: 
            - User's message (decrypted if it was encrypted)
            - User's role
            - AI's response (decrypted if it was encrypted)
            - AI's role (always 'assistant')
        """
        logging.debug(f"CLASS ChatDatabase - get_messages: Starting method for user: {username}.")
        
        if not self.is_connection_valid():
            logging.error("CLASS ChatDatabase - get_messages: Connection is not open!")
            logging.warning(f"CLASS ChatDatabase - get_messages: No messages will be returned for user: {username} due to inactive database connection.")
            return []
        
        try:
            with self.conn:
                logging.debug(f"CLASS ChatDatabase - get_messages: Attempting to execute SQL query to retrieve messages for user: {username}.")
                
                cursor = self.conn.execute("SELECT message, role, encrypted, response, response_encrypted FROM chat_sessions WHERE username = ?", (username,))
                
                messages = cursor.fetchall()
                
                logging.debug(f"CLASS ChatDatabase - get_messages: Retrieved {len(messages)} messages for user: {username}.")
                
                decrypted_messages = [
                    (
                        decrypt(message) if encrypted else message, 
                        role, 
                        decrypt(response) if response_encrypted else response, 
                        'assistant'
                    ) 
                    for message, role, encrypted, response, response_encrypted in messages
                ]
                
                logging.debug(f"CLASS ChatDatabase - get_messages: Decrypted messages for user: {username}.")
                logging.info(f"CLASS ChatDatabase - get_messages: Successfully retrieved messages for user: {username}.")
                
                return decrypted_messages
                
        except sqlite3.Error as e:
            logging.error(f"CLASS ChatDatabase - get_messages: Error retrieving messages: {e}")
            logging.warning(f"CLASS ChatDatabase - get_messages: No messages will be returned for user: {username} due to database error.")
            return []
        
        finally:
            logging.debug(f"CLASS ChatDatabase - get_messages: Exiting method for user: {username}.")

    def get_last_n_messages(self, n: int, user_name: str) -> list:
        """
        Retrieve the last n messages for a given username along with the AI's response.
        Enhanced with more detailed debugging logs.

        Parameters:
        - n (int): The number of messages to retrieve.
        - user_name (str): The name of the user.

        Returns:
        - A list of tuples containing the decrypted messages, role, and responses.
        """
        method_name = "get_last_n_messages"
        logging.debug(f"CLASS ChatDatabase - {method_name}: Method start.")
        logging.debug(f"CLASS ChatDatabase - {method_name}: Input parameters - username: {user_name}, n: {n}.")
        
        # Check connection status
        if not self.is_connection_valid():
            logging.error(f"CLASS ChatDatabase - {method_name}: No active connection to the database.")
            logging.debug(f"CLASS ChatDatabase - {method_name}: Attempting to reestablish connection...")
            self.open_connection()
            
            if not self.is_connection_valid():
                logging.error(f"CLASS ChatDatabase - {method_name}: Failed to reestablish connection. Exiting method.")
                return []
            else:
                logging.debug(f"CLASS ChatDatabase - {method_name}: Connection reestablished successfully.")
        
        try:
            sql_query = "SELECT message, role, encrypted, response, response_encrypted FROM chat_sessions WHERE username = ? ORDER BY id DESC LIMIT ?"
            logging.debug(f"CLASS ChatDatabase - {method_name}: Prepared SQL query: {sql_query}.")
            
            with self.conn:
                logging.debug(f"CLASS ChatDatabase - {method_name}: About to execute query with parameters - username: {user_name}, n: {n}.")
                cursor = self.conn.execute(sql_query, (user_name, n))
                
                if cursor:
                    messages = cursor.fetchall()
                    logging.debug(f"CLASS ChatDatabase - {method_name}: Raw fetched messages: {messages}.")
                    
                    if not messages:
                        logging.warning(f"CLASS ChatDatabase - {method_name}: No messages found for user: {user_name}.")
                    else:
                        logging.debug(f"CLASS ChatDatabase - {method_name}: Fetched {len(messages)} messages.")
                    
                    decrypted_messages = []
                    for message, role, encrypted, response, response_encrypted in messages:
                        decrypted_message = decrypt(message) if encrypted else message
                        decrypted_response = decrypt(response) if response_encrypted else response
                        
                        # Logging decryption status and results
                        logging.debug(f"CLASS ChatDatabase - {method_name}: Message decryption status - Encrypted: {encrypted}, Decrypted Message: {decrypted_message[:10]}...")
                        logging.debug(f"CLASS ChatDatabase - {method_name}: Response decryption status - Encrypted: {response_encrypted}, Decrypted Response: {decrypted_response[:10]}...")
                        
                        decrypted_messages.append((decrypted_message, role, decrypted_response))
                    
                    logging.debug(f"CLASS ChatDatabase - {method_name}: Decrypted messages: {decrypted_messages}.")
                    return decrypted_messages
                else:
                    logging.error(f"CLASS ChatDatabase - {method_name}: Failed to initialize cursor.")
                    return []
                
        except sqlite3.Error as e:
            logging.error(f"CLASS ChatDatabase - {method_name}: SQL error occurred - Type: {type(e).__name__}, Args: {e.args}.")
            return []
        
        finally:
            logging.debug(f"CLASS ChatDatabase - {method_name}: Finalizing method operations...")
            # If there are any other resources to close or finalize, they should be done here.
            logging.info(f"CLASS ChatDatabase - {method_name}: Method execution complete for user: {user_name}.")

    def close(self):
        """
        Closes the connection to the database.
        """
        logging.debug(f"CLASS ChatDatabase - close: Method entry for 'close'.")
        logging.debug(f"CLASS ChatDatabase - close: Initiating the closing procedure for database: {self.db_name}.")
        
        if self.is_connection_valid():
            logging.debug(f"CLASS ChatDatabase - close: Database connection status for {self.db_name}: Active.")
            logging.debug(f"CLASS ChatDatabase - close: Proceeding to close the connection to database: {self.db_name}.")
            
            try:
                self.close_connection()
                logging.debug(f"CLASS ChatDatabase - close: Successfully executed 'close_connection' for database: {self.db_name}.")
                logging.debug(f"CLASS ChatDatabase - close: Close connection procedure completed for database: {self.db_name}.")
            
            except ChatDatabaseError as e:
                logging.error(f"CLASS ChatDatabase - close: An error occurred while executing 'close_connection' for database: {self.db_name}. Error: {e}")
                logging.debug(f"CLASS ChatDatabase - close: Error details for database: {self.db_name}. Exception Type: {type(e).__name__}. Args: {e.args}.")
            
        else:
            logging.warning(f"CLASS ChatDatabase - close: Connection is either already closed or was never opened for database: {self.db_name}.")
            logging.debug(f"CLASS ChatDatabase - close: Skipping 'close_connection' procedure for database: {self.db_name}.")
        
        logging.debug(f"CLASS ChatDatabase - close: Method exit for 'close'.")




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
