import logging
import sqlite3
# Setting up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')

class EnhancedTestChatDatabase:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = None
        logging.debug(f"Initialized EnhancedTestChatDatabase with db_name: {db_name}")

    def open_connection(self):
        """Establish a connection to the database."""
        logging.debug(f"Attempting to open connection to {self.db_name}")
        self.conn = sqlite3.connect(self.db_name)
        logging.debug(f"Successfully opened connection to {self.db_name}")

    def close_connection(self):
        """Close the connection to the database."""
        if self.conn:
            logging.debug(f"Closing connection to {self.db_name}")
            self.conn.close()
            logging.debug(f"Closed connection to {self.db_name}")

    def get_last_n_messages(self, username: str, n: int = 10):
        """Retrieve the last n messages for a specified user."""
        if not self.conn:
            logging.error(f"Connection is not open. Database: {self.db_name}")
            raise Exception(f"Connection is not open. Database: {self.db_name}")

        logging.debug(f"Preparing to retrieve last {n} messages for user: {username}")
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT message FROM messages WHERE username=? ORDER BY timestamp DESC LIMIT ?", (username, n))
        
        # Retrieve messages and close cursor
        messages = cursor.fetchall()
        logging.debug(f"Retrieved {len(messages)} messages for user: {username}")
        cursor.close()
        
        return messages

# Sample execution for enhanced debugging
enhanced_db_tester = EnhancedTestChatDatabase("DB\chat.db")
enhanced_db_tester.open_connection()
messages = enhanced_db_tester.get_last_n_messages("Matthew David Schafer")
enhanced_db_tester.close_connection()

messages
