"""
Title: User Authentication and Chat Application (PilotPro)
Description: 
This Python script implements a Proof of Concept (POC) chat application called PilotPro. It allows users to register, log in, manage user roles, reset passwords, and engage in chat interactions with an AI.

Author: Matthew Schafer
Date: August 31, 2023
Company: VE7LTX Diagonal Thinking LTD

Requirements:
- Python 3.x
- Required packages: uuid, datetime, os, sqlite3, bcrypt, cryptography, dotenv, [other required packages]
- External modules: chat_utils, chat_db
- Additional Python packages: altgraph==0.17.3, anyio==3.7.1, [for other packages check the requirements.txt file]

Usage:
1. Ensure the required packages are installed using 'pip install [package name]'.
2. Set up a SQLite database with the necessary tables.
3. Customize constants and configurations as needed.
4. Run the script using 'python [regi.py]'.

Logic Breakdown:
- This script defines a chat application that incorporates user authentication and interaction with an AI.
- The app uses a modular structure with classes for handling different aspects of the application.

Module Usage:
- `Database` Class:
  - Base class for database operations.
  - Provides methods to create a connection, execute queries, and fetch data.

- `RegiDatabase` Class:
  - Extends `Database` to handle user registration-specific database operations.
  - Manages the 'users' table for user data storage.
  - Encrypts and decrypts user details using `CryptoHandler`.

- `CryptoHandler` Class:
  - Handles encryption and decryption of sensitive data.
  - Uses the Fernet cryptography library for secure data handling.

- `SessionManager` Class:
  - Manages user session creation, validation, and termination.
  - Creates session entries in the 'sessions' table.
  - Ensures sessions expire after a set duration.

- `UserManager` Class:
  - Manages user-related operations such as registration, authentication, role management, and password reset.
  - Uses bcrypt for secure password storage and comparison.
  - Provides methods for admin functions like adding and deleting users.

- `App` Class:
  - Serves as the main application controller.
  - Initializes instances of `RegiDatabase`, `UserManager`, and `SessionManager`.
  - Provides a menu-based user interface for interaction.
  - Handles user login, logout, role-based actions, and chat initiation.

Header Comment Explanation:
- This script outlines a user authentication and chat application called PilotPro.
- Users can register, log in, engage in chat interactions with an AI, and perform administrative tasks.
- Data is stored in a SQLite database with encryption for sensitive user information.
- The app promotes security by utilizing bcrypt for password handling and Fernet for encryption.
- User sessions are managed for a specified duration, enhancing user experience and security.
- Role-based access control allows users to perform actions based on their assigned roles.
- The script's modular structure improves maintainability and scalability.
- Developers should follow best practices for production use, including further security enhancements.
"""
import uuid
import datetime
import os
import sqlite3
import bcrypt
import logging
from cryptography.fernet import Fernet
from dotenv import load_dotenv, set_key
from typing import Optional, Union
from chat_utils import ChatSession
from chat_db import ChatDatabase

# Constants
DEFAULT_DB_NAME = ".\\DB\\users.db"
SESSION_DURATION = 30  # Session duration in minutes
ROLES = ['general', 'admin']

# Load and setup encryption key
load_dotenv()
if not os.getenv("ENCRYPTION_KEY"):
    set_key(".env", "ENCRYPTION_KEY", Fernet.generate_key().decode())

KEY = os.getenv("ENCRYPTION_KEY").encode()
cipher_suite = Fernet(KEY)


class Database:
    """Base class for database operations."""

    def __init__(self, db_name=DEFAULT_DB_NAME):
        self.db_name = db_name
        logging.debug(f"CLASS Database - __init__: Initializing Database with database name: {db_name}")
        if not os.path.exists(".\\DB"):
            os.makedirs(".\\DB")
            logging.debug(f"CLASS Database - __init__: Created database directory: .\\DB")
        else:
            logging.debug(f"CLASS Database - __init__: Database directory .\\DB already exists.")
        self.create_connection()

    def create_connection(self):
        """Create a database connection and return the connection object."""
        logging.debug(f"CLASS Database - create_connection: Attempting to create connection to database: {self.db_name}")
        try:
            conn = sqlite3.connect(self.db_name)
            logging.debug(f"CLASS Database - create_connection: Successfully connected to the database: {self.db_name}")
            return conn
        except sqlite3.Error as e:
            logging.exception(f"CLASS Database - create_connection: sqlite3 Error while connecting to {self.db_name}")
            print(e)

    def execute_query(self, query: str, parameters: tuple = ()):
        """Execute a single query."""
        logging.debug(f"CLASS Database - execute_query: Attempting to execute query: {query} with parameters: {parameters}")
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, parameters)
            conn.commit()
            logging.debug(f"CLASS Database - execute_query: Query executed successfully on {self.db_name}")

    def fetch_one(self, query: str, parameters: tuple = ()) -> Union[tuple, None]:
        """Fetch a single record from the database."""
        logging.debug(f"CLASS Database - fetch_one: Fetching one record using query: {query} with parameters: {parameters}")
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, parameters)
            result = cursor.fetchone()
            logging.debug(f"CLASS Database - fetch_one: Fetched record: {result}")
            return result

    def fetch_all(self, query: str, parameters: tuple = ()) -> list:
        """Fetch all records from the database."""
        logging.debug(f"CLASS Database - fetch_all: Fetching all records using query: {query} with parameters: {parameters}")
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, parameters)
            results = cursor.fetchall()
            logging.debug(f"CLASS Database - fetch_all: Fetched {len(results)} records from {self.db_name}")
            return results


class RegiDatabase(Database):
    def __init__(self, db_name=DEFAULT_DB_NAME):
        logging.debug(f"CLASS RegiDatabase - __init__: Initializing RegiDatabase with database name: {db_name}")
        super().__init__(db_name)
        self.create_encryption_keys_table()
        self.create_users_table()  # Ensure that the users table is created on initialization

    def create_encryption_keys_table(self):
        """Create the encryption_keys table if it doesn't exist."""
        logging.debug("CLASS RegiDatabase - create_encryption_keys_table: Attempting to create encryption_keys table.")
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS encryption_keys (
                    username TEXT PRIMARY KEY,
                    encrypted_user_key TEXT
                )
            """)
            connection.commit()
            logging.debug("CLASS RegiDatabase - create_encryption_keys_table: encryption_keys table created/check completed.")

    def store_encrypted_user_key(self, username: str, encrypted_user_key: bytes):
        """Store the encrypted user-specific key in the database."""
        logging.debug(f"CLASS RegiDatabase - store_encrypted_user_key: Storing encrypted user key for username: {username}")
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO encryption_keys (username, encrypted_user_key) VALUES (?, ?)",
                           (username, encrypted_user_key))
            conn.commit()
            logging.debug(f"CLASS RegiDatabase - store_encrypted_user_key: Encrypted user key stored for username: {username}")

    def fetch_encrypted_user_key(self, username: str) -> Union[bytes, None]:
        """Fetch the encrypted user-specific key from the database."""
        logging.debug(f"CLASS RegiDatabase - fetch_encrypted_user_key: Fetching encrypted user key for username: {username}")
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT encrypted_user_key FROM encryption_keys WHERE username = ?", (username,))
            encrypted_user_key = cursor.fetchone()
            if encrypted_user_key:
                logging.debug(f"CLASS RegiDatabase - fetch_encrypted_user_key: Encrypted user key fetched for username: {username}")
            else:
                logging.warning(f"CLASS RegiDatabase - fetch_encrypted_user_key: No encrypted user key found for username: {username}")
            return encrypted_user_key[0] if encrypted_user_key else None

    def create_users_table(self):
        logging.debug("CLASS RegiDatabase - create_users_table: Attempting to create users table.")
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    encrypted_first_name TEXT,
                    encrypted_middle_name TEXT,
                    encrypted_last_name TEXT,
                    encrypted_full_name TEXT,
                    encrypted_email TEXT
                )
            ''')
            conn.commit()
            logging.debug("CLASS RegiDatabase - create_users_table: users table created/check completed.")

    def decrypt_data(self, encrypted_data: bytes, username: str) -> str:
        """
        Decrypts user details using the CryptoHandler.
        """
        logging.debug(f"CLASS RegiDatabase - decrypt_data: Decrypting data for username: {username}")
        encrypted_user_key = self.fetch_encrypted_user_key(username)
        if not encrypted_user_key:
            logging.error(f"CLASS RegiDatabase - decrypt_data: No encryption key found for user {username}.")
            raise ValueError("No encryption key found for user.")

        user_key = CryptoHandler.decrypt_user_key(encrypted_user_key, KEY)
        decrypted_data = CryptoHandler.decrypt_detail_with_key(encrypted_data, user_key)
        logging.debug(f"CLASS RegiDatabase - decrypt_data: Successfully decrypted data for username: {username}")
        return decrypted_data
    
    
class CryptoHandler:
    @staticmethod
    def generate_user_key(self):
        """Generate a new encryption key for a user."""
        logging.debug("CLASS CryptoHandler - generate_user_key: Starting method.")
        try:
            user_key = Fernet.generate_key()
            logging.debug("CLASS CryptoHandler - generate_user_key: Encryption key generated successfully: %s", user_key)
            return user_key
        except Exception as e:
            logging.exception("CLASS CryptoHandler - generate_user_key: Exception occurred during key generation: %s", e)
            return None

    @staticmethod
    def encrypt_user_key(user_key: bytes, main_key: bytes) -> bytes:
        """Encrypt a user-specific key using the main encryption key."""
        logging.debug("CLASS CryptoHandler - encrypt_user_key: Starting method.")
        try:
            logging.debug("CLASS CryptoHandler - encrypt_user_key: Main key: %s", main_key)
            fernet = Fernet(main_key)
            encrypted_user_key = fernet.encrypt(user_key)
            logging.debug("CLASS CryptoHandler - encrypt_user_key: User-specific key encrypted successfully: %s", encrypted_user_key)
            return encrypted_user_key
        except Exception as e:
            logging.exception("CLASS CryptoHandler - encrypt_user_key: Exception occurred during encryption: %s", e)
            return None

    @staticmethod
    def decrypt_user_key(encrypted_user_key: bytes, main_key: bytes) -> bytes:
        """Decrypt a user-specific key using the main encryption key."""
        logging.debug("CLASS CryptoHandler - decrypt_user_key: Starting method.")
        try:
            logging.debug("CLASS CryptoHandler - decrypt_user_key: Main key: %s", main_key)
            fernet = Fernet(main_key)
            decrypted_user_key = fernet.decrypt(encrypted_user_key)
            logging.debug("CLASS CryptoHandler - decrypt_user_key: Encrypted user-specific key decrypted successfully: %s", decrypted_user_key)
            return decrypted_user_key
        except Exception as e:
            logging.exception("CLASS CryptoHandler - decrypt_user_key: Exception occurred during decryption: %s", e)
            return None

    @staticmethod
    def encrypt_detail_with_key(detail: str, user_key: bytes) -> bytes:
        """Encrypts a detail (like a name) using a user-specific key."""
        logging.debug(f"CLASS CryptoHandler - encrypt_detail_with_key: Starting method.")
        try:
            logging.debug(f"CLASS CryptoHandler - encrypt_detail_with_key: Detail to encrypt: {detail}")
            fernet = Fernet(user_key)
            encrypted_detail = fernet.encrypt(detail.encode('utf-8'))
            logging.debug("CLASS CryptoHandler - encrypt_detail_with_key: Detail encrypted successfully: %s", encrypted_detail)
            return encrypted_detail
        except Exception as e:
            logging.exception("CLASS CryptoHandler - encrypt_detail_with_key: Exception occurred during encryption: %s", e)
            return None

    @staticmethod
    def decrypt_detail_with_key(encrypted_detail: bytes, user_key: bytes) -> str:
        """Decrypts an encrypted detail using a user-specific key."""
        logging.debug("CLASS CryptoHandler - decrypt_detail_with_key: Starting method.")
        try:
            logging.debug("CLASS CryptoHandler - decrypt_detail_with_key: Decrypting encrypted detail.")
            fernet = Fernet(user_key)
            decrypted_detail = fernet.decrypt(encrypted_detail).decode('utf-8')
            logging.debug(f"CLASS CryptoHandler - decrypt_detail_with_key: Encrypted detail decrypted to: {decrypted_detail}.")
            return decrypted_detail
        except Exception as e:
            logging.exception("CLASS CryptoHandler - decrypt_detail_with_key: Exception occurred during decryption: %s", e)
            return None

    
class SessionManager:
    """Handles user session management."""
    def __init__(self, db_name: str):
        self.db_name = db_name
        logging.debug(f"CLASS SessionManager: Beginning initialization with database: {db_name}")
        self.create_sessions_table()
        logging.debug(f"CLASS SessionManager: Completed initialization with database: {db_name}")


    def create_session(self, username: str, role: str) -> tuple[str, str]:
        logging.debug(f"CLASS SessionManager - create_session: Starting session creation for username: {username} with role: {role}")
        
        session_id = str(uuid.uuid4())
        logging.debug(f"CLASS SessionManager - create_session: Generated session ID: {session_id}")
        
        expiration = (datetime.datetime.now() + 
                    datetime.timedelta(minutes=SESSION_DURATION)).strftime('%Y-%m-%d %H:%M:%S')
        logging.debug(f"CLASS SessionManager - create_session: Calculated expiration time for session: {expiration}")
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            logging.debug(f"CLASS SessionManager - create_session: Preparing to insert session details into database")
            cursor.execute(
                "INSERT INTO sessions (session_id, username, role, expiration) VALUES (?, ?, ?, ?)", 
                (session_id, username, role, expiration)
            )
            conn.commit()
            logging.debug(f"CLASS SessionManager - create_session: Session details inserted into the database successfully")
        
        logging.info(f"CLASS SessionManager - create_session: Session created successfully for username: {username} with session ID: {session_id} and expiration: {expiration}")
        return session_id, username

    
    def create_sessions_table(self):
        """Create the sessions table if it doesn't already exist."""
        logging.debug("CLASS SessionManager - create_sessions_table: Starting process to check or create sessions table.")
        
        try:
            with sqlite3.connect(self.db_name) as connection:
                logging.debug("CLASS SessionManager - create_sessions_table: Database connection established.")
                cursor = connection.cursor()
                
                logging.debug("CLASS SessionManager - create_sessions_table: Preparing SQL statement for sessions table creation.")
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    username TEXT,
                    role TEXT,
                    expiration TEXT
                )
                """
                
                cursor.execute(create_table_sql)
                logging.debug("CLASS SessionManager - create_sessions_table: SQL statement executed.")
                
                connection.commit()
                logging.debug("CLASS SessionManager - create_sessions_table: Changes committed to the database.")
                
                logging.info("CLASS SessionManager - create_sessions_table: Sessions table check and creation process completed successfully.")
                
        except sqlite3.Error as e:
            logging.error("CLASS SessionManager - create_sessions_table: SQLite error occurred: %s", e)
        except Exception as ex:
            logging.error("CLASS SessionManager - create_sessions_table: An unexpected error occurred: %s", ex)
            
    def validate_session(self, session_id: str) -> tuple:
        """Validates the session and returns a tuple of (is_valid, role)"""
        logging.debug(f"CLASS SessionManager - validate_session: Validating session with session ID: {session_id}")
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT expiration, role FROM sessions WHERE session_id=?", (session_id,))
            session = cursor.fetchone()

        if session:
            expiration = datetime.datetime.strptime(session[0], '%Y-%m-%d %H:%M:%S')
            if datetime.datetime.now() > expiration:
                logging.warning(f"CLASS SessionManager - validate_session: Session {session_id} has expired.")
                self.terminate_session(session_id)
                return (False, None)
            logging.debug(f"CLASS SessionManager - validate_session: Session {session_id} is valid.")
            return (True, session[1])
        logging.warning(f"CLASS SessionManager - validate_session: No session found with session ID: {session_id}.")
        return (False, None)

    def terminate_session(self, session_id: str):
        """Deletes the session from the database."""
        logging.debug(f"CLASS SessionManager - terminate_session: Initiating termination process for session with ID: {session_id}")
        
        with sqlite3.connect(self.db_name) as conn:
            logging.debug(f"CLASS SessionManager - terminate_session: Successfully connected to the database: {self.db_name}")
            
            cursor = conn.cursor()
            logging.debug("CLASS SessionManager - terminate_session: Cursor created. Preparing to execute DELETE statement.")
            
            # Ensure session_id is passed as a single-element tuple
            params = (session_id,)
            cursor.execute("DELETE FROM sessions WHERE session_id=?", params)
            logging.debug(f"CLASS SessionManager - terminate_session: DELETE statement executed for session ID: {session_id}. Preparing to commit changes.")
            
            conn.commit()
            logging.debug(f"CLASS SessionManager - terminate_session: Changes committed to the database. Session with ID: {session_id} has been removed.")
        
        logging.info(f"CLASS SessionManager - terminate_session: Termination process completed for session with ID: {session_id}.")


class UserManager:
    def __init__(self, db: RegiDatabase):
        logging.debug("CLASS UserManager: Initializing UserManager class.")
        self.db = db
        logging.debug(f"CLASS UserManager: Database object of type {type(db)} assigned to the instance.")
        
        self.crypto_handler = CryptoHandler()
        logging.debug(f"CLASS UserManager: CryptoHandler object of type {type(self.crypto_handler)} created and assigned to the instance.")
        
        logging.info("CLASS UserManager: UserManager initialized successfully.")

    def register_user(self, username: str, password: str, full_name: str, email: str, role: str):
        """Register a new user with the given details."""
        logging.debug(f"CLASS UserManager - register_user: Starting user registration for username: {username}")

        if role not in ROLES:
            logging.error(f"CLASS UserManager - register_user: Invalid role provided: {role}")
            raise ValueError(f"Invalid role provided: {role}. Valid roles are {', '.join(ROLES)}.")

        with sqlite3.connect(self.db.db_name) as conn:
            cursor = conn.cursor()

            names = full_name.split()
            logging.debug(f"CLASS UserManager - register_user: Splitting full name into: {names}")

            user_key = self.crypto_handler.generate_user_key()  # Generate user-specific key
            logging.debug(f"CLASS UserManager - register_user: User-specific key generated for username: {username}")

            encrypted_first_name = CryptoHandler.encrypt_detail_with_key(names[0], user_key)
            encrypted_last_name = CryptoHandler.encrypt_detail_with_key(names[-1], user_key)
            encrypted_middle_name = CryptoHandler.encrypt_detail_with_key(' '.join(names[1:-1]), user_key) if len(names) > 2 else ""
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            encrypted_email = CryptoHandler.encrypt_detail_with_key(email, user_key)
            encrypted_full_name = CryptoHandler.encrypt_detail_with_key(full_name, user_key)
            
            logging.debug(f"CLASS UserManager - register_user: All user details encrypted for username: {username}")

            try:
                cursor.execute("INSERT INTO users (username, password, role, encrypted_first_name, encrypted_middle_name, encrypted_last_name, encrypted_full_name, encrypted_email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                            (username, hashed_password, role, encrypted_first_name, encrypted_middle_name, encrypted_last_name, encrypted_full_name, encrypted_email))
                conn.commit()

                # Encrypt and store the user-specific key
                encrypted_user_key = self.crypto_handler.encrypt_user_key(user_key, KEY)
                self.db.store_encrypted_user_key(username, encrypted_user_key)

                logging.info(f"CLASS UserManager - register_user: User {full_name} registered successfully!")
                print(f"User {full_name} registered successfully!")
                return True
            except sqlite3.IntegrityError:
                logging.error(f"CLASS UserManager - register_user: Registration failed due to IntegrityError for username: {username}")
                return False


    def authenticate_user(self, username: str, password: str) -> Optional[tuple]:
        """Authenticate the user and return their full name and role if successful."""
        with sqlite3.connect(self.db.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password, role, encrypted_first_name, encrypted_middle_name, encrypted_last_name, encrypted_full_name FROM users WHERE username=?", (username,))
            user = cursor.fetchone()

        # Fetch the encrypted user-specific key for the given username
        encrypted_user_key = self.db.fetch_encrypted_user_key(username)

        if not encrypted_user_key:
            return None

        # Decrypt the user-specific key using the main encryption key
        user_key = CryptoHandler.decrypt_user_key(encrypted_user_key, KEY)

        if user and bcrypt.checkpw(password.encode('utf-8'), user[0]):
            role = user[1]
            decrypted_first_name = CryptoHandler.decrypt_detail_with_key(user[2], user_key)
            decrypted_middle_name = CryptoHandler.decrypt_detail_with_key(user[3], user_key) if user[3] else ""
            decrypted_last_name = CryptoHandler.decrypt_detail_with_key(user[4], user_key)
            decrypted_full_name = CryptoHandler.decrypt_detail_with_key(user[5], user_key)
            return (decrypted_full_name, role)
        return None

    def set_user_role(self, username: str, new_role: str) -> None:
        with sqlite3.connect(self.db.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
            conn.commit()

    def delete_user(self, username: str) -> None:
        """
        Perform a clean delete of a user and all related database items.
        
        Args:
            username (str): The username of the user to be deleted.
        """
        with sqlite3.connect(self.db.db_name) as conn:
            cursor = conn.cursor()
            
            # Delete user's session
            cursor.execute("DELETE FROM sessions WHERE username = ?", (username,))
            
            # TODO: Delete any other related records in other tables
            
            # Delete the user
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            
            conn.commit()

    def reset_password(self, username: str, new_password: str) -> None:
        """Reset the password for a user."""
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        with sqlite3.connect(self.db.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = ? WHERE username = ?", 
                           (hashed_password, username))
            conn.commit()
            
    def add_user_by_admin(self, username: str, full_name: str, email: str, role: str):
        """Admin adds a new user with a default password."""
        default_password = "pilotpro"
        self.register_user(username, default_password, full_name, email, role)
        print(f"User {full_name} added successfully with default password: {default_password}")


class App:
    def __init__(self):
        self.db = RegiDatabase()
        self.user_manager = UserManager(self.db)
        self.session_manager = SessionManager(self.db.db_name)
        self.current_session = None
        self.current_user_role = None
        
    def main_menu(self):
        while True:
            print("\n--- Main Menu ---")

            if not self.current_session:
                print("(r)egister")
                print("(l)ogin")
                print("(x)it")
            else:
                print("(z) To Logout to Main Menu")
                print("(x)it and logout")

                if self.current_user_role == 'admin':
                    print("(d)elete user")
                    print("(a)dd user")

                print("(s)tart chat")

                if self.current_user_role == 'admin':
                    print("(m)odify user role")

                print("(p)change password")

            choice = input("Please enter your choice: ").lower()
            self.handle_choice(choice)

    def handle_choice(self, choice):
        if not self.current_session:
            if choice == 'r':
                self.register()
            elif choice == 'l':
                self.login()
            elif choice == 'x':
                self.exit_app()
            else:
                print("Invalid choice. Please try again.")
        else:
            if choice == 'z':
                self.logout()
            elif choice == 'x':
                self.exit_app()
            elif choice == 's':
                # Fetch user details using the current session's username
                with sqlite3.connect(self.db.db_name) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT encrypted_full_name FROM users WHERE username=?", (self.current_session[1],))

                    user_details = cursor.fetchone()

                # Diagnostic print to check the fetched user_details
                # print(f"Debug: Fetched user_details = {user_details}")

                if user_details:
                    decrypted_full_name = self.db.decrypt_data(user_details[0], self.current_session[1])
                    self.start_chat(decrypted_full_name)
                else:
                    print("Error: User details not found.")
                    
            elif self.current_user_role == 'admin':
                if choice == 'd':
                    self.delete_user()
                elif choice == 'a':
                    self.admin_add_user()
                elif choice == 'm':
                    self.modify_user_role()
                else:
                    print("Invalid choice. Please try again.")
            elif choice == 'p':
                self.change_password()
            else:
                print("Invalid choice. Please try again.")

    def login(self):
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        user = self.user_manager.authenticate_user(username, password)
        if user:
            decrypted_full_name = user[0]
            logging.info(f"Hello {decrypted_full_name}! (Full name: {decrypted_full_name})")
            self.decrypted_full_name = decrypted_full_name  # Store it as an instance variable

            self.current_user_role = user[1]
            self.current_session = self.session_manager.create_session(username, self.current_user_role)

            # Log the successful login event to the chat database
            with ChatDatabase() as db:
                db.insert_message(username, "User logged in", "system")

            logging.debug(f"Current Session ID = {self.current_session}")
            logging.debug(f"Current User Role = {self.current_user_role}")

            # Set logging level to DEBUG for admin users
            if self.current_user_role == "admin":
                logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.warning("Login failed for username: %s", username)  # Log warning for failed login
            print("Login failed.")

    def change_password(self):
        """Allows the user to change their password."""
        if not self.current_session:
            print("You need to be logged in to change your password.")
            return
        
        old_password = input("Enter your current password: ")
        
        # Authenticate the user using the old password
        user = self.user_manager.authenticate_user(self.current_session.username, old_password)
        
        if not user:
            print("Incorrect current password. Please try again.")
            return
        
        new_password = input("Enter your new password: ")
        confirm_password = input("Confirm your new password: ")

        if new_password == confirm_password:
            # Update the user's password in the database
            self.user_manager.reset_password(self.current_session.username, new_password)
            print("Password changed successfully!")
        else:
            print("New passwords do not match. Please try again.")

    def modify_user_role(self):
        target_username = input("Enter the username of the user you wish to modify: ")
        new_role = input(f"Enter the new role ({'/'.join(ROLES)}) for the user: ").lower()
        
        while new_role not in ROLES:
            print("Invalid role. Please try again.")
            new_role = input(f"Enter the new role ({'/'.join(ROLES)}): ").lower()

        self.user_manager.set_user_role(target_username, new_role)
        print(f"Role for user {target_username} has been set to {new_role}.")

    def admin_add_user(self):
        username = input("Enter a username for the new user: ")
        full_name = input("Enter the full name (First [Middle(s)] Last) for the new user: ")
        email = input("Enter the email for the new user: ")
        role = input(f"Enter the role ({'/'.join(ROLES)}) for the new user: ").lower()
        while role not in ROLES:
            print("Invalid role. Please try again.")
            role = input(f"Enter your role ({'/'.join(ROLES)}): ").lower()
        self.user_manager.add_user_by_admin(username, full_name, email, role)

    def reset_password(self):
        if not self.current_session:
            print("You need to be logged in to reset your password.")
            return
        new_password = input("Enter your new password: ")
        confirm_password = input("Confirm your new password: ")
        if new_password != confirm_password:
            print("Passwords do not match. Please try again.")
            return
        # Assuming the username is stored in the session (this might need to be adjusted based on the actual implementation)
        self.user_manager.reset_password(self.current_session.username, new_password)
        print("Password reset successfully!")
        
    def register(self):
        """Handle user registration."""
        while True:  # Keep prompting until a unique username is provided
            username = input("Enter a username: ")
            password = input("Enter a password: ")
            full_name = input("Enter your full name (First [Middle(s)] Last): ")
            email = input("Enter your email: ")
            
            # Check if the email contains the string 've7ltx'
            if 've7ltx' in email:
                role = 'admin'
            else:
                role = 'general'

            success = self.user_manager.register_user(username, password, full_name, email, role)
            
            if success:
                break  # Exit the loop if registration was successful
            else:
                print("Sorry, username taken. Please try again.")

    def delete_user(self):
        username_to_delete = input("Enter the username of the user you wish to delete: ")

        # Check the total number of admins in the database
        total_admins = self.db.fetch_all("SELECT COUNT(*) FROM users WHERE role = 'admin'")

        # Check if the user to be deleted is an admin
        user_to_delete = self.db.fetch_one("SELECT role FROM users WHERE username = ?", (username_to_delete,))
        if not user_to_delete:
            print(f"User {username_to_delete} does not exist.")
            return

        if user_to_delete[0] == 'admin' and total_admins[0][0] <= 1:
            print("Cannot delete the last admin. Operation aborted.")
            return

        confirm = input(f"Are you sure you want to delete {username_to_delete}? (y/n): ").lower()
        if confirm == 'y':
            self.user_manager.delete_user(username_to_delete)
            print(f"User {username_to_delete} has been deleted.")
        else:
            print("User deletion aborted.")

    def logout(self):
        print("Logged out successfully!")
        self.session_manager.terminate_session(self.current_session)
        self.current_session = None
        self.current_user_role = None

    def exit_app(self):
        if self.current_session:
            print("Logging out and exiting the program. Goodbye!")
            self.session_manager.terminate_session(self.current_session)
        else:
            print("Goodbye!")
        exit(0)
        
    def start_chat(self, decrypted_full_name: str):
        """
        Initiates a chat session for the user.
        """
        if self.current_session:
            chat_session = ChatSession(decrypted_full_name)
            print(f"\n{decrypted_full_name} Impeccable Taste! I'm Calling up your Chat Interface Now. Please remember you can type 'help' for a list of commands at any time.")
            chat_session.start()
        else:
            print("Error: User not logged in.")


if __name__ == "__main__":
    app = App()
    app.main_menu()

# ----------------- FOOTER ------------------
# End of regi.py
# 
# Accomplishments:
# 1. Role-based user management with secure authentication.
# 2. Encrypted data storage for sensitive user information.
# 3. Dynamic session management with expiration functionality.
# 4. Modular design promoting scalability and maintainability.
# 5. Integrated chat functionality for user interaction with AI.
#
# Areas for Improvement:
# 1. Implement multi-factor authentication for added security.
# 2. Enhance logging mechanisms for better traceability and diagnostics.
# 3. Address potential deprecated functions and ensure compatibility with future Python versions.
# 4. Optimize database operations for efficiency.
# 
# Security Reminder:
# Ensure secure storage and management of encryption keys.
# Regularly update encryption mechanisms to stay abreast with industry standards.
# Avoid hardcoding sensitive information; always use environment variables or secure vaults.
#
# ----------------- FOOTER ------------------
