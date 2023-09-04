import sys
sys.path.append('..')  # Add the parent directory to the path

import unittest
import os
from chat_db import ChatDatabase, encrypt, decrypt
from chat_utils import ContextManager 
def setUp(self):
    """Prepare environment for testing."""
    self.db_name = "test_chat.db"
    self.context_manager = ContextManager()  # Create an instance of ContextManager
    self.chat_db = ChatDatabase(context_manager=self.context_manager, db_name=self.db_name)  # Pass the context_manager instance

class TestChatDatabase(unittest.TestCase):
    
    def setUp(self):
        """Prepare environment for testing."""
        self.db_name = "test_chat.db"
        self.chat_db = ChatDatabase(db_name=self.db_name)

    def tearDown(self):
        """Clean up after tests."""
        # Close database connection
        self.chat_db.close()
        
        # Remove test database
        if os.path.exists(self.db_name):
            os.remove(self.db_name)

    def test_connection_and_table_creation(self):
        """Test database connection and table creation."""
        self.assertTrue(self.chat_db.is_connection_valid())

    def test_insert_and_retrieve_message(self):
        """Test inserting a message and retrieving it."""
        # Insert a message
        username = "test_user"
        message = "Hello, world!"
        role = "user"
        response = "Hello, user!"
        self.chat_db.insert_message(username, message, role, response)

        # Retrieve the message
        messages = self.chat_db.get_messages(username)
        self.assertTrue(messages)  # Assert that we got a non-empty list
        retrieved_message, retrieved_role, retrieved_response, _ = messages[0]
        self.assertEqual(retrieved_message, message)
        self.assertEqual(retrieved_role, role)
        self.assertEqual(retrieved_response, response)

    def test_message_encryption(self):
        """Test inserting an encrypted message and retrieving its decrypted form."""
        username = "test_encryption"
        message = "Encrypt this!"
        role = "user"
        response = "Encrypted reply."
        self.chat_db.insert_message(username, message, role, response)

        # Retrieve and check decryption
        messages = self.chat_db.get_messages(username)
        decrypted_message, _, decrypted_response, _ = messages[0]
        self.assertEqual(decrypted_message, message)
        self.assertEqual(decrypted_response, response)

    def test_retrieve_last_n_messages(self):
        """Test retrieving the last n messages."""
        username = "test_last_n"
        for i in range(5):
            self.chat_db.insert_message(username, f"Message {i}", "user", f"Response {i}")

        # Retrieve the last 3 messages
        last_messages = self.chat_db.get_last_n_messages(3, username)
        self.assertEqual(len(last_messages), 3)
        self.assertEqual(last_messages[0][0], "Message 4")  # Latest message

    def test_invalid_input(self):
        """Test behavior with invalid input."""
        with self.assertRaises(ValueError):
            self.chat_db.insert_message("", "No username", "user", "Invalid!")

        with self.assertRaises(ValueError):
            self.chat_db.get_messages("")

        with self.assertRaises(ValueError):
            decrypt("")

        with self.assertRaises(ValueError):
            encrypt(None)

    def test_non_existent_message_retrieval(self):
        """Test behavior when trying to retrieve a non-existent message."""
        messages = self.chat_db.get_messages("non_existent_user")
        self.assertFalse(messages)  # Should get an empty list

# Continue with other tests if necessary ...

if __name__ == "__main__":
    unittest.main()
