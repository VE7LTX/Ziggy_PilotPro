"""
chat_utils.py
-------------

Description:
    The `chat_utils.py` module offers a suite of tools designed to enhance and streamline chat sessions between 
    users and two AI models: a primary AI (Personal AI) and a secondary backup (GPT-4). This module places emphasis 
    on maintaining a dynamic chat context to offer more tailored responses based on previous interactions.

Key Components:
    - ContextManager: Orchestrates the dynamic generation of context for the AI, drawing from past user-AI interactions.
    - ChatUtility: Facilitates the actual chat communication between the user and both AI models.
    - ChatSession: Manages individual chat sessions, processes user commands, and integrates AI functionalities.

Features:
    - Adaptable context generation to leverage recent chat interactions.
    - Capability to add custom context details like user's name and current time.
    - Dual AI integration: Primary (Personal AI) and Secondary (GPT-4) for redundancy.
    - Comprehensive logging system for effective debugging.
    - In-session user commands (help, logs, exit) for enhanced user experience.

Workflow:
    1. Initiate chat session with user identification.
    2. Incorporate user's name into the chat context.
    3. Process user input:
       a. Handle in-session commands.
       b. Direct chat inputs to the primary AI.
       c. Utilize secondary AI in case of primary AI failure or inadequate response.
    4. Display AI response to the user.
    5. Repeat until the session is terminated by the user.

Dependencies:
    - requests: To manage API requests.
    - logging: For effective debugging and error tracking.
    - chat_db: For database operations and fetching recent chat messages.
    - constants: Houses critical constant values like API endpoints and headers.

Author: Matthew Schafer
Date: August 31, 2023
Company: VE7LTX Diagonal Thinking LTD
"""

import requests
from typing import Optional, List, Dict
from chat_db import ChatDatabase
from constants import DOMAINNAME, BASE_URL, HEADERS, OPENAI_HEADERS, OPENAI_ENDPOINT


import logging
import io
import datetime
import json



log_stream = io.StringIO()
logging.basicConfig(level=logging.DEBUG, stream=log_stream)


class ContextManager:
    def __init__(self):
        self.db = ChatDatabase(ContextManager)
        self.custom_context = ("You are an amazing AI Lifeform, called Pilot Pro. "
                               "Your job is to help as best you can with simple instructions and complete info.")
        self.username = ""
        self.full_name = ""

    def generate_context(self, username: str = None, full_name: str = None) -> str:
        """Generates a context string combining recent messages, custom context, and user's full name."""
        
        if username:
            self.username = username
        if full_name:
            self.full_name = full_name
        
        recent_messages = self._get_recent_messages(self.username)
        context_messages = " ".join(recent_messages)

        context = f"{context_messages} {self.custom_context} The user's name is {self.full_name}."
        context = context.strip()  # Remove any leading or trailing spaces

        logging.debug(f"Generated context for username {self.username}: {context}")
        return context

    def _get_recent_messages(self, username: str) -> list:
        """Retrieve recent messages for a given username."""
        try:
            messages = self.db.get_last_n_messages(10, username)
            decrypted_messages = [self.db.decrypt(message[0]) for message in messages]
            return decrypted_messages
        except Exception as e:
            logging.error(f"Error retrieving recent messages for {username}: {e}")
            return []

    def add_custom_context(self, custom_context: str) -> None:
        """Append additional custom context."""
        try:
            self.custom_context += f" {custom_context}"
            logging.debug(f"Added custom context: {custom_context}")
        except Exception as e:
            logging.error(f"Error adding custom context: {e}")

    def remember_username_and_full_name(self, username: str, full_name: str) -> None:
        """Store the provided username and full name."""
        self.username = username
        self.full_name = full_name
        logging.debug(f"Stored username: {username} and full name: {full_name}")

    def add_current_time_context(self) -> None:
        """Add the current time to the custom context."""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.add_custom_context(f"The current time is {current_time}.")

    def check_for_time_keywords(self, message: str) -> bool:
        """Check if the message contains time-related keywords."""
        time_keywords = ['time', 'date', 'day', 'month', 'year', 'hour', 'minute', 'second']
        return any(keyword in message for keyword in time_keywords)


    def update_context(self, last_message_sent: str, last_message_received: str, username: Optional[str] = None) -> None:
        """Update the context based on the last message sent and received."""
        self.add_custom_context(f"Last sent message: {last_message_sent}.")
        self.add_custom_context(f"Last received message: {last_message_received}.")

        # Use the username if provided
        if username:
            self.add_custom_context(f"Username: {username}.")

        if self.check_for_time_keywords(last_message_sent):
            self.add_current_time_context()


class ChatUtility:
    def __init__(self, username: str, user_full_name: str, db: ChatDatabase):
        self.username = username
        self.full_name = user_full_name
        self.db = db
        self.context_manager = ContextManager()

    def send_primary_PAI(self, text: str, domain_name: str = "ms", context: Optional[str] = None) -> Dict:
        try:
            logging.debug(f"send_primary_PAI: Starting method with text={text}, domain_name={domain_name}, context={context}")
            
            # Update the context using the last message sent
            self.context_manager.update_context(self.username, text, None)
            
            # Generate context if not provided
            context = context or self.context_manager.generate_context(self.username, self.full_name)
            
            recent_interactions_tuples = self.db.get_last_n_messages(10, self.username)
            recent_interactions = [message[0] for message in recent_interactions_tuples]
            logging.debug(f"send_primary_PAI: Recent interactions fetched: {recent_interactions}")

            # Prepare the payload
            payload = {
                "Text": text,
                "DomainName": domain_name,
                "Context": context
            }
            
            logging.debug(f"send_primary_PAI: Sending request with payload: {payload}")
            response = requests.post(BASE_URL + "/message", headers=HEADERS, json=payload, timeout=60)
            
            logging.debug(f"send_primary_PAI: Response headers: {response.headers}")
            logging.debug(f"send_primary_PAI: Response text: {response.text}")
            
            if response.status_code != 200:
                raise ValueError(f"API returned {response.status_code}: {response.text}")

            response_data = response.json()
            
            ai_message = response_data.get('ai_message')
            ai_score = response_data.get('ai_score')

            # Save both user's message and AI's response
            self.db.save_message(self.username, text, 'User')
            if ai_message:
                self.db.save_message(self.username, ai_message, 'AI')

            return {
                "response": ai_message,
                "score": ai_score,
                "source": "Personal AI",
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }

        except Exception as e:
            logging.error(f"send_primary_PAI: An error occurred: {e}")
            return {"error": str(e)}

    def send_secondary_GPT4(self, prompt: str, context: Optional[str] = None, recent_interactions: Optional[List[str]] = None) -> str:
        try:
            # Update the context using the last message sent
            self.context_manager.update_context(self.username, prompt, None)
            
            # Generate context if not provided
            context = context or self.context_manager.generate_context(self.username, self.full_name)
            
            recent_interactions_tuples = self.db.get_last_n_messages(10, self.username)
            recent_interactions = [message[0] for message in recent_interactions_tuples]

            
            messages = [{"role": "system", "content": context}]
            messages.extend([{"role": "system", "content": interaction[0]} for interaction in recent_interactions])
            
            # Prepare the payload
            payload = {
                "model": "gpt-4",
                "messages": messages
            }

            response = requests.post(OPENAI_ENDPOINT, headers=OPENAI_HEADERS, json=payload, timeout=30)
            if response.status_code != 200:
                raise ValueError(f"API returned {response.status_code}: {response.text}")

            response_data = response.json()
            ai_content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()

            # Save both user's message and AI's response
            self.db.save_message(self.username, prompt, 'User')
            if ai_content:
                self.db.save_message(self.username, ai_content, 'AI')

            return ai_content
        except Exception as e:
            logging.error(f"send_secondary_GPT4: An error occurred: {e}")
            return "An error occurred while processing the request."

class ChatSession:
    def __init__(self, username: str, full_name: str):
        logging.debug("CLASS ChatSession - __init__: Initialization started.")
        logging.debug(f"CLASS ChatSession - __init__: Received username: {username}")
        logging.debug(f"CLASS ChatSession - __init__: Received full name: {full_name}")

        self.username = username
        self.full_name = full_name  # This is used for display in the chat
        logging.debug("CLASS ChatSession - __init__: Assigned instance variables.")

        self.db = ChatDatabase(ContextManager)
        logging.debug("CLASS ChatSession - __init__: ChatDatabase instance created.")

        # Assuming ChatUtility needs the username for database operations or similar tasks
        self.chat_utility = ChatUtility(self.username, self.full_name, self.db)
        logging.debug("CLASS ChatSession - __init__: ChatUtility instance created with the provided username.")

        self.commands = {
            'help': self._show_help,
            'logs': self._fetch_recent_logs,
            'exit': self._exit_session
        }
        logging.debug("CLASS ChatSession - __init__: Commands dictionary initialized.")
        logging.debug("CLASS ChatSession - __init__: Initialization completed.")

    def _show_help(self):
        print("""
        Chat App Help
        -------------
        
        Welcome to the Chat App, your gateway to an AI assistant. Use the following commands to navigate and interact with the system:

        - help: Display this help message.
        
        - logs: View the last 25 debugging log items. Useful for troubleshooting.
        
        - exit: Safely terminate the current chat session and exit the Chat Interface and go to the Main Settings Menu.

        Note: Always type commands without quotes or slashes.
        """)

    def _fetch_recent_logs(self):
        """
        Fetch and display the last 25 log messages from the logging module 
        and the last 25 messages from the chat database.
        """
        
        # Fetch the last 25 log messages from the logging module
        for handler in logging.root.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream is log_stream:
                logs = log_stream.getvalue().split('\n')[-25:]
                print("=== Last 25 Log Messages ===")
                print('\n'.join(logs))
                print("="*30)
        
        # Fetch the last 25 messages from the chat database
        try:
            db = ChatDatabase()
            recent_messages = db.get_last_n_messages(25, self.full_name)  # use self.full_name
            print("=== Last 25 Chat Messages ===")
            for message in recent_messages:
                print(message)
            print("="*30)
        except Exception as e:
            print(f"Error fetching messages from the database: {e}")

    def _exit_session(self):
        print("Thank you for chatting! Goodbye!")
        return 'exit'
    
    def _process_command(self, command: str):
        func = self.commands.get(command)
        if func:
            return func(self)

    def _get_response(self, user_message: str):
        try:
            # Pass the correct arguments to send_primary_PAI
            response_data = self.chat_utility.send_primary_PAI(user_message, self.full_name)

            # If there's an issue with the primary AI or the response is empty, fallback to secondary AI
            if not response_data["response"]:
                logging.info("\nSwitching to secondary AI due to empty response from primary AI.")
                return self.chat_utility.send_secondary_GPT4(user_message, self.full_name)

            return response_data["response"]
        except requests.exceptions.Timeout as e:
            logging.error(f"Timeout error: {e}")
            return "Sorry, the request timed out. Please try again later."
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error: {e}")
            return "Sorry, a network error occurred while processing your request."
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return "Sorry, an unexpected error occurred while processing your request."
        
    def start(self):
        self.chat_utility.context_manager.remember_username_and_full_name(username=self.username, full_name=self.full_name)
        print("\nWelcome to the Pilot Pro Chat (PROOF OF CONCEPT), Hosted by Ziggy the Personal.ai of Matthew Schafer! \nType 'help' for available commands or 'exit' to exit the chat to the Main Settings Menu.")
        
        while True:
            try:
                user_message = input(f"\n{self.full_name}: ")
                print(f"DEBUG: User input: {user_message}")  # Debug print

                # Update context with the recent message
                self.chat_utility.context_manager.update_context(username=self.username, 
                                                                last_message_sent=user_message, 
                                                                last_message_received="")

                if user_message in self.commands:
                    command_result = self._process_command(user_message)
                    if command_result == 'exit':
                        break
                    continue

                response = self._get_response(user_message)
                print(f"DEBUG: AI response: {response}")  # Debug print

                # Update context with the recent response
                self.chat_utility.context_manager.update_context(username=self.username, 
                                                                last_message_sent=user_message, 
                                                                last_message_received=response)
                
                print(f"\nPilot Pro AI: {response}\n")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                print("Sorry, an unexpected error occurred. Please try again.")

# -----------------------------------------------------------------------------
# End of `chat_utils.py` module.
#
# Overview:
# - This module is vital for the PilotPro chat application, ensuring seamless interaction between users and AIs.
# - It emphasizes on offering a dynamic chat experience by maintaining and updating chat context.
# - The dual AI integration ensures redundancy and reliability.
# - With built-in user commands, the chat experience is designed to be user-centric and intuitive.
#
# Tips for Future Development:
# - Enhancements can be made in the context generation to offer even more tailored responses.
# - Consider adding more in-session user commands for added functionality.
# - Regularly update API endpoints and keys in the constants module for security.
# - Always prioritize user privacy and data security, especially when dealing with chat logs.
# - Regularly test with new AI models for improved chat interactions.
#
# Remember: Effective logging and commenting are crucial for troubleshooting and future development.
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
