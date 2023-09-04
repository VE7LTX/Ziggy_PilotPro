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
    encrypted_message = ""
    try:
        for c in message:
            encrypted_char = chr(ord(c) + 3)
            encrypted_message += encrypted_char

        return encrypted_message
    except Exception as e:
        raise

def decrypt(encrypted_message: str) -> str:
    """
    Decrypts the given encrypted message by subtracting 3 from the ordinal value of each character.

    Parameters:
    - encrypted_message (str): The encrypted message to be decrypted.

    Returns:
    - str: The decrypted message.
    """
    if not encrypted_message or not isinstance(encrypted_message, str):
        return ""
    
    try:
        decrypted_chars = [chr(ord(c) - 3) for c in encrypted_message]
        decrypted_message = ''.join(decrypted_chars)
        return decrypted_message
    except Exception as e:
        raise

    
    
class ChatDatabase:
    def __init__(self, db_name: str = "chat.db"):
        logging.debug(f"CLASS ChatDatabase - __init__: Method entry. Initializing ChatDatabase.")
        
        self.db_folder = "DB"  # Default folder name
        logging.debug(f"CLASS ChatDatabase - __init__: Setting default database folder to: {self.db_folder}")

        logging.debug(f"CLASS ChatDatabase - __init__: Checking existence of database directory: {self.db_folder}")
        # Ensure the DB folder exists or create it
        if not os.path.exists(self.db_folder):
            logging.debug(f"CLASS ChatDatabase - __init__: Database directory {self.db_folder} does not exist. Attempting to create it.")
            
            os.makedirs(self.db_folder)
            logging.debug(f"CLASS ChatDatabase - __init__: Successfully created database directory: {self.db_folder}")
        else:
            logging.debug(f"CLASS ChatDatabase - __init__: Database directory {self.db_folder} already exists. No need to create.")
        
        self.db_name = os.path.join(self.db_folder, db_name)
        logging.debug(f"CLASS ChatDatabase - __init__: Constructed database path: {self.db_name}")

        self.conn = None
        logging.debug(f"CLASS ChatDatabase - __init__: Initialized database connection variable to None.")
        
        logging.debug(f"CLASS ChatDatabase - __init__: ChatDatabase initialized successfully with database path: {self.db_name}")
        logging.debug(f"CLASS ChatDatabase - __init__: Method exit.")


    def __enter__(self):
        logging.debug(f"CLASS ChatDatabase - __enter__: Preparing to enter context management for database: {self.db_name}.")
        
        self.open_connection()

        if self.conn:
            logging.debug(f"CLASS ChatDatabase - __enter__: Successfully opened a connection to database: {self.db_name}.")
        else:
            logging.error(f"CLASS ChatDatabase - __enter__: Failed to open a connection to database: {self.db_name}.")

        logging.info(f"CLASS ChatDatabase - __enter__: Entered context management for database: {self.db_name}.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logging.debug(f"CLASS ChatDatabase - __exit__: Preparing to exit context management for database: {self.db_name}.")

        if exc_type or exc_value or traceback:
            logging.error(f"CLASS ChatDatabase - __exit__: Exception detected during context management. Type: {exc_type}, Value: {exc_value}.")
            logging.debug(f"CLASS ChatDatabase - __exit__: Traceback: {traceback}")

        self.close_connection()

        if not self.conn:
            logging.debug(f"CLASS ChatDatabase - __exit__: Successfully closed connection to database: {self.db_name}.")
        else:
            logging.error(f"CLASS ChatDatabase - __exit__: Failed to close connection to database: {self.db_name}.")

        logging.info(f"CLASS ChatDatabase - __exit__: Exited context management for database: {self.db_name}.")

    def open_connection(self):
        logging.debug(f"CLASS ChatDatabase - open_connection: Starting method to handle database connection.")

        # Initial log for the connection attempt
        logging.debug(f"CLASS ChatDatabase - open_connection: Preparing to open connection to database: {self.db_name}")

        # Check if the database file exists before attempting to connect
        if not os.path.exists(self.db_name):
            logging.warning(f"CLASS ChatDatabase - open_connection: Database file {self.db_name} does not exist. Will be created upon connection.")

        # Check if there is an existing connection
        if not self.conn:
            try:
                logging.debug(f"CLASS ChatDatabase - open_connection: Attempting to establish a connection to database: {self.db_name}")
                self.conn = sqlite3.connect(self.db_name)
                logging.debug(f"CLASS ChatDatabase - open_connection: Successfully established connection to database: {self.db_name}")

                # Check and create tables
                logging.debug(f"CLASS ChatDatabase - open_connection: Checking and creating necessary tables in database: {self.db_name}")
                self._create_tables()
                logging.debug(f"CLASS ChatDatabase - open_connection: Tables checked/created successfully in database: {self.db_name}")

            except sqlite3.OperationalError as oe:
                logging.error(f"CLASS ChatDatabase - open_connection: Operational Error while attempting to connect to {self.db_name}. Error: {oe}")
                logging.debug(f"CLASS ChatDatabase - open_connection: Checking if database file {self.db_name} is accessible and not locked by another process.")

            except sqlite3.Error as e:
                logging.error(f"CLASS ChatDatabase - open_connection: sqlite3 Error while attempting to connect to {self.db_name}. Error: {e}")
                logging.debug(f"CLASS ChatDatabase - open_connection: Verifying database file integrity and structure.")

            except Exception as e:
                logging.exception(f"CLASS ChatDatabase - open_connection: Unexpected Error while attempting to connect to {self.db_name}. Error: {e}")
                logging.debug(f"CLASS ChatDatabase - open_connection: Checking environmental factors and external dependencies.")
            
        else:
            logging.warning(f"CLASS ChatDatabase - open_connection: Connection already active to database: {self.db_name}. Consider closing the current connection before opening a new one.")

        logging.debug(f"CLASS ChatDatabase - open_connection: Ending method after handling database connection.")


    def close_connection(self):
        """
        Close the database connection.
        """
        logging.debug(f"CLASS ChatDatabase - close_connection: Method entry.")
        logging.info(f"CLASS ChatDatabase - close_connection: Attempting to close connection to database: {self.db_name}")
        
        if self.conn:
            logging.debug(f"CLASS ChatDatabase - close_connection: Active connection found for database: {self.db_name}.")
            try:
                self.conn.close()
                logging.debug(f"CLASS ChatDatabase - close_connection: Connection closed successfully for database: {self.db_name}")
            except sqlite3.OperationalError as oe:
                logging.error(f"CLASS ChatDatabase - close_connection: Operational Error while closing: {oe}")
                logging.debug(f"CLASS ChatDatabase - close_connection: Verifying database integrity after Operational Error.")
            except sqlite3.Error as e:
                logging.error(f"CLASS ChatDatabase - close_connection: sqlite3 Error while closing: {e}")
                logging.debug(f"CLASS ChatDatabase - close_connection: Verifying database connections and cursors after sqlite3 Error.")
            except Exception as e:
                logging.exception(f"CLASS ChatDatabase - close_connection: Unexpected Error while closing: {e}")
                logging.debug(f"CLASS ChatDatabase - close_connection: Verifying database state after Unexpected Error.")
            finally:
                self.conn = None
                logging.debug(f"CLASS ChatDatabase - close_connection: Connection variable reset to None for database: {self.db_name}.")
                logging.info(f"CLASS ChatDatabase - close_connection: Final state of connection is: {self.conn}")
        else:
            logging.warning(f"CLASS ChatDatabase - close_connection: Connection is already closed or was never initialized for database: {self.db_name}")
            logging.debug(f"CLASS ChatDatabase - close_connection: Skipping connection close procedure.")

        logging.debug(f"CLASS ChatDatabase - close_connection: Method exit.")

    def _create_tables(self):
        """
        Create tables if they don't exist.
        """
        # Starting the table creation/checking process
        logging.debug("CLASS ChatDatabase - _create_tables: Starting the table creation/checking process.")

        # Checking if there's an active connection
        if not self.conn:
            logging.error("CLASS ChatDatabase - _create_tables: No active database connection.")
            return

        try:
            # Using a context manager for the database connection
            logging.debug("CLASS ChatDatabase - _create_tables: Preparing to execute SQL for table creation/checking.")
            
            with self.conn:
                # SQL statement to create the table if it doesn't exist
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
            # Logging the successful execution of the SQL statement
            logging.debug("CLASS ChatDatabase - _create_tables: SQL execution for table creation/checking was successful.")

        except sqlite3.OperationalError as oe:
            logging.error(f"CLASS ChatDatabase - _create_tables: Operational Error during table creation/checking. Error: {oe}")
            logging.debug("CLASS ChatDatabase - _create_tables: Verifying 'chat_sessions' table structure.")
        except sqlite3.IntegrityError as ie:
            logging.error(f"CLASS ChatDatabase - _create_tables: Integrity Error during table creation/checking. Error: {ie}")
            logging.debug("CLASS ChatDatabase - _create_tables: Verifying table constraints.")
        except sqlite3.Error as e:
            # Logging the error along with the traceback
            logging.exception(f"CLASS ChatDatabase - _create_tables: General SQLite error during table creation/checking.")
        except Exception as e:
            logging.exception(f"CLASS ChatDatabase - _create_tables: An unexpected error occurred during table creation/checking. Error: {e}")

        # Indicating the end of the process
        logging.debug("CLASS ChatDatabase - _create_tables: Table creation/checking process complete.")


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
        if not self.conn:
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

        except sqlite3.IntegrityError as ie:
            logging.error(f"CLASS ChatDatabase - insert_message: Integrity Error for user: {username}. Possibly a primary key conflict. Error: {ie}.")
        except sqlite3.OperationalError as oe:
            logging.error(f"CLASS ChatDatabase - insert_message: Operational Error for user: {username}. Error: {oe}.")
            logging.debug(f"CLASS ChatDatabase - insert_message: Verifying 'chat_sessions' table structure in database: {self.db_name}.")
        except sqlite3.Error as e:
            logging.exception(f"CLASS ChatDatabase - insert_message: General sqlite3 error occurred for user: {username}. Error: {e}.")
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
        
        if not self.conn:
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

    def get_last_n_messages(self, username: str, n: int) -> List[Tuple[str, str]]:
        """
        Retrieve the last 'n' interactions (messages and responses) for a given username.
        
        Args:
        - username (str): The name of the user.
        - n (int): The number of interactions to retrieve.

        Returns:
        - List of tuples containing: 
            - User's message (decrypted if it was encrypted)
            - AI's response (decrypted if it was encrypted)
        """
        logging.debug(f"CLASS ChatDatabase - get_last_n_messages: Retrieving last {n} messages for user: {username}.")
        
        if not self.conn:
            logging.error("CLASS ChatDatabase - get_last_n_messages: Connection is not open!")
            return []
        
        try:
            with self.conn:
                cursor = self.conn.execute(
                    "SELECT message, encrypted, response, response_encrypted FROM chat_sessions WHERE username = ? ORDER BY id DESC LIMIT ?",
                    (username, n)
                )
                
                interactions = cursor.fetchall()
                decrypted_interactions = [
                    (
                        decrypt(message) if encrypted else message, 
                        decrypt(response) if response_encrypted else response
                    ) 
                    for message, encrypted, response, response_encrypted in interactions
                ]
                
                logging.debug(f"CLASS ChatDatabase - get_last_n_messages: Retrieved {len(decrypted_interactions)} interactions for user: {username}.")
                return decrypted_interactions
                
        except sqlite3.Error as e:
            logging.error(f"CLASS ChatDatabase - get_last_n_messages: Error retrieving messages: {e}")
            return []
                        
    def get_last_interaction(self, username: str) -> Tuple[str, str]:
        """
        Retrieve the last interaction (message and response) for a given username.
        """
        method_name = "get_last_interaction"
        logging.debug(f"CLASS ChatDatabase - {method_name}: Method start.")
        logging.debug(f"CLASS ChatDatabase - {method_name}: Input parameter - username: {username}.")
        
        # Check connection status
        if not self.conn:
            logging.error(f"CLASS ChatDatabase - {method_name}: No active connection to the database.")
            logging.debug(f"CLASS ChatDatabase - {method_name}: Attempting to reestablish connection...")
            self.open_connection()
            
            if not self.conn:
                logging.error(f"CLASS ChatDatabase - {method_name}: Failed to reestablish connection. Exiting method.")
                return ("", "")
        
        try:
            sql_query = "SELECT message, encrypted, response, response_encrypted FROM chat_sessions WHERE username = ? ORDER BY id DESC LIMIT 1"
            logging.debug(f"CLASS ChatDatabase - {method_name}: Prepared SQL query: {sql_query}.")
            
            with self.conn:
                logging.debug(f"CLASS ChatDatabase - {method_name}: About to execute query with parameters.")
                cursor = self.conn.execute(sql_query, (username,))
                interaction = cursor.fetchone()
                
                if not interaction:
                    logging.warning(f"CLASS ChatDatabase - {method_name}: No interaction found for user: {username}.")
                    return ("", "")
                
                message, encrypted, response, response_encrypted = interaction
                decrypted_message = decrypt(message) if encrypted else message
                decrypted_response = decrypt(response) if response_encrypted else response
                
                logging.debug(f"CLASS ChatDatabase - {method_name}: Decrypted interaction: ({decrypted_message}, {decrypted_response}).")
                
                return (decrypted_message, decrypted_response)
            
        except sqlite3.Error as e:
            logging.error(f"CLASS ChatDatabase - {method_name}: SQL error occurred - Type: {type(e).__name__}, Args: {e.args}.")
            return ("", "")



    def close(self):
        logging.debug(f"CLASS ChatDatabase - close: Method entry for 'close'.")
        logging.debug(f"CLASS ChatDatabase - close: Initiating the closing procedure for database: {self.db_name}.")
        
        if self.conn:
            logging.debug(f"CLASS ChatDatabase - close: Database connection status for {self.db_name}: Active.")
            logging.debug(f"CLASS ChatDatabase - close: Proceeding to close the connection to database: {self.db_name}.")
            
            try:
                self.close_connection()
                logging.debug(f"CLASS ChatDatabase - close: Successfully executed 'close_connection' for database: {self.db_name}.")
                logging.debug(f"CLASS ChatDatabase - close: Close connection procedure completed for database: {self.db_name}.")
            
            except Exception as e:
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
