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
from constants import *
from chat_db import ChatDatabase as Database
import logging
import io
import datetime
import json



log_stream = io.StringIO()
logging.basicConfig(level=logging.DEBUG, stream=log_stream)

class ContextManager:
    def __init__(self):
        logging.debug("CLASS ContextManager - __init__: Initializing ContextManager...")
        self.db = Database()
        self.custom_context = []  # Using a list to make appending easier and more efficient

    def generate_context(self, username: str, full_name: str) -> str:
        """Generate context based on recent interactions and custom context."""
        logging.debug(f"CLASS ContextManager - generate_context: Starting method for user: {full_name}.")
        try:
            recent_interactions = self.db.get_messages(username)
            logging.debug(f"CLASS ContextManager - generate_context: Recent interactions fetched for {full_name}: {recent_interactions}.")
        except Exception as e:
            logging.error(f"CLASS ContextManager - generate_context: Error retrieving interactions for {full_name}: {e}.")
            recent_interactions = []

        # Combining recent interactions and custom context
        context = " ".join(recent_interactions + self.custom_context)
        logging.debug(f"CLASS ContextManager - generate_context: Final context for {full_name}: {context[:100]}...")  # Display only first 100 chars for brevity
        return context

    def add_context(self, context: str) -> None:
        """Append to the custom context."""
        logging.debug(f"CLASS ContextManager - add_context: Starting method.")
        logging.debug(f"CLASS ContextManager - add_context: Appending to custom context: {context}.")
        self.custom_context.append(context)

    def add_name_context(self, full_name: str) -> None:
        logging.debug(f"CLASS ContextManager - add_name_context: Starting method for {full_name}.")
        self.add_context(f"The user's name is {full_name}.")

    def add_current_time_context(self) -> None:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.debug(f"CLASS ContextManager - add_current_time_context: Starting method. Current time: {current_time}.")
        self.add_context(f"The current time is {current_time}.")

    def add_last_session_time_context(self, last_session_time: str) -> None:
        logging.debug(f"CLASS ContextManager - add_last_session_time_context: Starting method. Last session time: {last_session_time}.")
        self.add_context(f"The last session was at {last_session_time}.")

    def add_last_message_context(self, sent: str, received: str) -> None:
        logging.debug(f"CLASS ContextManager - add_last_message_context: Starting method. Sent: {sent}, Received: {received}.")
        self.add_context(f"The last message sent was: {sent}.")
        self.add_context(f"The last message received was: {received}.")

    def add_last_n_messages_context(self, n: int, username: str) -> None:
        logging.debug(f"CLASS ContextManager - add_last_n_messages_context: Starting method. Fetching last {n} messages for user with username {username}...")
        try:
            last_n_messages = self.db.get_messages(username)[:n]
            logging.debug(f"CLASS ContextManager - add_last_n_messages_context: Last {n} messages fetched for {username}: {last_n_messages}.")
            for message in last_n_messages:
                self.add_context(message)
        except Exception as e:
            logging.error(f"CLASS ContextManager - add_last_n_messages_context: Error adding last {n} messages for user with username {username}: {e}.")

    # The remaining methods stay the same, but you can apply similar changes to them

# Ensure logging is configured for debugging
logging.basicConfig(level=logging.DEBUG)

    
    
class ChatUtility:
    def __init__(self, db: Database = None):
        self.db = db or Database()
        self.context_manager = ContextManager()


    def send_primary_PAI(self, text: str, username: str, full_name: str, domain_name: str = "ms", context: Optional[str] = None) -> Dict:
        logging.debug("Entering send_primary_PAI method.")
        logging.debug(f"Parameters: text='{text}', username='{username}', full_name='{full_name}', domain_name='{domain_name}', context='{context}'.")

        try:
            with self.db:
                # Get the last 10 pairs of chat interactions for context
                if not context:
                    logging.debug("Context not provided. Generating context using context_manager.")
                    context = self.context_manager.generate_context(username, full_name)  # Pass both username and full_name

                payload = {
                    "Text": text,
                    "DomainName": domain_name,
                    "Context": context
                }

                logging.debug(f"Payload for request: {payload}")
                response = requests.post(BASE_URL + "/message", headers=HEADERS, json=payload, timeout=60)
                logging.debug(f"Received response with status code {response.status_code}")

                response_data = response.json()
                logging.debug(f"Response data: {json.dumps(response_data, indent=4)}")

                ai_message = response_data.get('ai_message', None)
                ai_score = response_data.get('ai_score', None)  # Extracting ai_score

                result = {
                    "response": ai_message,
                    "score": ai_score,
                    "source": "Personal AI",
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }
                logging.debug(f"Constructed result: {result}")
                logging.debug("Exiting send_primary_PAI method.")
                return result

        except requests.RequestException as e:
            logging.error(f"Request error: {e}")
            raise  # Re-raise the exception after logging
        except Exception as e:
            logging.error(f"Unexpected error in send_primary_PAI: {e}")
            raise  # Re-raise the exception after logging

 

    def send_secondary_GPT4(self, prompt: str, username: str, full_name: str, context: Optional[str] = None, recent_interactions: Optional[List[str]] = None) -> str:
        with self.db:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }

            messages = [{"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"{prompt}"}]

            if not context:
                context = self.context_manager.generate_context(username, full_name)
            
            print("OPENAI DEBUG: Context generated")

            if not recent_interactions:
                recent_interactions = self.db.get_last_n_messages(10, username)
            
            print("OPENAI DEBUG: Recent interactions fetched")

            messages.append({"role": "system", "content": context})
            messages.extend([{"role": "system", "content": interaction} for interaction in recent_interactions])

            payload = {
                "model": "gpt-4",
                "messages": messages
            }

            print(f"OPENAI DEBUG: Sending payload: {payload}")

            response = requests.post(OPENAI_ENDPOINT, headers=headers, json=payload, timeout=30)
            
            print(f"OPENAI DEBUG: Response received: {response.text}")

            response_data = response.json()
            ai_content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()

            return ai_content

class ChatSession:
    def __init__(self, username: str, user_full_name: str):
        self.username = username
        self.full_name = user_full_name
        self.chat_utility = ChatUtility()
        self.commands = {
            'help': self._show_help,
            'logs': self._fetch_recent_logs,
            'exit': self._exit_session
        }

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
            db = Database()
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
            return func()

    def _get_response(self, user_message: str):
        try:
            # Pass the correct arguments to send_primary_PAI
            response_data = self.chat_utility.send_primary_PAI(user_message, self.username, self.full_name)


            # If there's an issue with the primary AI or the response is empty, fallback to secondary AI
            if not response_data["response"]:
                logging.info("\nSwitching to secondary AI due to empty response from primary AI.")
                return self.chat_utility.send_secondary_GPT4(user_message, self.username, self.full_name)


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
        self.chat_utility.context_manager.add_name_context(self.full_name)
        print("\nWelcome to the Pilot Pro Chat (PROOF OF CONCEPT), Hosted by Ziggy the Personal.ai of Matthew Schafer! \nType 'help' for available commands or 'exit' to exit the chat to the Main Settings Menu.")
        while True:
            try:
                user_message = input(f"\n{self.full_name}: ")

                if user_message in self.commands:
                    command_result = self._process_command(user_message)
                    if command_result == 'exit':
                        break
                    continue

                response = self._get_response(user_message)
                print(f"\nPilot Pro AI: {response}\n")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                print("Sorry, an unexpected error occurred. Please try again.")

# -----------------------------------------------------------------------------
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
