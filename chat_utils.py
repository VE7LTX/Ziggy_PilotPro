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
        self.db = Database()
        self.custom_context = ""  # Initialize custom_context attribute

    def generate_context(self, username: str) -> str:
        """Generate context based on the last 5 message pairs in history and any custom context."""
        
        # Logging the start of the method with input details.
        logging.debug(f"generate_context DEBUG Starting method. Generating context for username: {username}")
        
        # Attempting to retrieve recent interactions.
        try:
            recent_interactions = self.db.get_last_n_messages(10, username)
            
            # Log a warning if no recent interactions are found for the given user.
            if not recent_interactions:
                logging.warning(f"generate_context DEBUG No recent interactions found for username: {username}")
                
            logging.debug(f"generate_context DEBUG Recent interactions retrieved for username {username}: {recent_interactions}")
            
        except Exception as e:
            # Log detailed error information if there's an exception while retrieving recent interactions.
            logging.error(f"generate_context DEBUG Error retrieving recent interactions for username {username}")
            logging.error("Exception Type: %s", type(e).__name__)
            logging.error("Exception Args: %s", e.args)
            logging.error("Recommendation: Check the get_last_n_messages method and the database connection.")
            recent_interactions = []
        
        # Constructing the context string.
        context = f"".join(recent_interactions)
        context += f"{self.custom_context}"
        
        # Logging the final constructed context.
        logging.debug(f"generate_context DEBUG Final constructed context for username {username}: {context}")
        
        return context


    # TODO - add date and time to context if keywords for date and time are found in the last message inputted by the user
    
    def add_custom_context(self, custom_context: str) -> None:
        """Add custom context."""
        
        # Logging the start of the method with the input details.
        logging.debug(f"CLASS ContextManager - add_custom_context: Starting method. Attempting to add custom context: {custom_context}")
        
        # Try to add the custom context to the existing context.
        try:
            self.custom_context += f"Your an amazing AI Lifeform, Called Pilot Pro, your job is to help as best you can with simple instructions and complete info. {custom_context}"
            
            # Log the success of adding the custom context.
            logging.debug(f"CLASS ContextManager - add_custom_context: Successfully added custom context: {custom_context}")
            
        except Exception as e:
            # Log detailed error information if there's an exception while adding custom context.
            logging.error(f"CLASS ContextManager - add_custom_context: Error adding custom context.")
            logging.error("Exception Type: %s", type(e).__name__)
            logging.error("Exception Args: %s", e.args)
            logging.error("Recommendation: Check the custom_context input and ensure it's a valid string.")
        
        # Log the final state of the custom context.
        logging.debug(f"CLASS ContextManager - add_custom_context: Final state of custom context: {self.custom_context}")



    def add_name_context(self, name: str) -> None:
        """Add the user's name to the context."""
        logging.debug(f"CLASS ContextManager - add_name_context: Adding name {name} to context.")
        self.add_custom_context(f"The user's name is {name}.")
        logging.debug(f"CLASS ContextManager - add_name_context: Name context added.")

    def add_current_time_context(self) -> None:
        """Add the current time to the context."""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.debug(f"CLASS ContextManager - add_current_time_context: Adding current time {current_time} to context.")
        self.add_custom_context(f"The current time is {current_time}.")
        logging.debug(f"CLASS ContextManager - add_current_time_context: Current time context added.")

    def add_last_session_time_context(self, last_session_time: str) -> None:
        """Add the time of the last session to the context."""
        logging.debug(f"CLASS ContextManager - add_last_session_time_context: Adding last session time {last_session_time} to context.")
        self.add_custom_context(f"The last session was at {last_session_time}.")
        logging.debug(f"CLASS ContextManager - add_last_session_time_context: Last session time context added.")

    def add_last_message_context(self, last_message_sent: str, last_message_received: str) -> None:
        """Add the last message sent and received to the context."""
        logging.debug(f"CLASS ContextManager - add_last_message_context: Adding last messages to context.")
        self.add_custom_context(f"The last message sent was: {last_message_sent}")
        self.add_custom_context(f"The last message received was: {last_message_received}")
        logging.debug(f"CLASS ContextManager - add_last_message_context: Last message context added.")

    def add_last_n_messages_context(self, n: int, username: str) -> None:
        """Add the last n messages to the context."""
        
        # Logging the start of the method with input details.
        logging.debug(f"CLASS ContextManager - add_last_n_messages_context: Starting method. Attempting to add the last {n} messages for {username} to context.")
        
        try:
            # Fetch the last n messages.
            last_n_messages = self.db.get_last_n_messages(n, username)
            
            # Log the fetched messages.
            logging.debug(f"CLASS ContextManager - add_last_n_messages_context: Fetched the last {n} messages for {username}: {last_n_messages}")
            
            # Add the fetched messages to the custom context.
            self.add_custom_context("\n".join(last_n_messages))
            
            # Log the success of adding the last n messages to the context.
            logging.debug(f"CLASS ContextManager - add_last_n_messages_context: Successfully added the last {n} messages for {username} to context.")
            
        except Exception as e:
            # Log detailed error information if there's an exception while adding the last n messages to the context.
            logging.error(f"CLASS ContextManager - add_last_n_messages_context: Error adding the last {n} messages for {username} to context.")
            logging.error("Exception Type: %s", type(e).__name__)
            logging.error("Exception Args: %s", e.args)
            logging.error("Recommendation: Check the database connection and ensure the structure of the 'chat_sessions' table matches the query.")
        
        # Log the final state of the custom context.
        logging.debug(f"CLASS ContextManager - add_last_n_messages_context: Final state of custom context: {self.custom_context}")


    def add_last_session_messages_context(self, username: str) -> None:
        """Add the last two message pairs from the last session to the context."""
        # Placeholder for the logic to get the last two message pairs from the last session.
        # This will depend on how you're storing sessions in your database.
        logging.warning("CLASS ContextManager - add_last_session_messages_context: Method not yet implemented.")


    # More context manipulation methods can be added here.
    
    
class ChatUtility:
    def __init__(self, db: Database = None):
        self.db = db or Database()
        self.context_manager = ContextManager()

    def send_primary_PAI(self, text: str, username: str, domain_name: str = "ms", context: Optional[str] = None) -> Dict:
        with self.db:
            # Get the last 10 pairs of chat interactions for context
            if not context:
                context = self.context_manager.generate_context(username)
            
            payload = {
                "Text": text,
                "DomainName": domain_name,
                "Context": context
            }

            print(f"\n THIS IS A TEMPORARY PAI DEBUG: \nThis is the payload we are sending: \n{payload}\n")

            response = requests.post(BASE_URL + "/message", headers=HEADERS, json=payload, timeout=60)
            
#            print(f"PAI DEBUG: Response status code: {response.status_code}")
#            print(f"PAI DEBUG: Response received: {response.text}")
#            print(f"PAI DEBUG: Response JSON: {json.dumps(response.json(), indent=4)}")
            response_data = response.json()
            
            # Debug the entire response JSON
#            print(f"PAI DEBUG: Entire Response JSON: {json.dumps(response_data, indent=4)}")
            '''
            # Check if 'ai_message' key exists and its value
            if 'ai_message' in response_data:
                print(f"PAI DEBUG: 'ai_message' key found. Value: {response_data['ai_message']}")
            else:
                print("PAI DEBUG: 'ai_message' key not found in response.")

            # Check if 'ai_score' key exists and its value
            if 'ai_score' in response_data:
                print(f"PAI DEBUG: 'ai_score' key found. Value: {response_data['ai_score']}")
            else:
                print("PAI DEBUG: 'ai_score' key not found in response.")
'''
            ai_message = response_data.get('ai_message', None)
            ai_score = response_data.get('ai_score', None)  # Extracting ai_score

            return {
                "response": ai_message,
                "score": ai_score,  # Including ai_score in the returned dictionary
                "source": "Personal AI",
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }

    def send_secondary_GPT4(self, prompt: str, username: str, context: Optional[str] = None, recent_interactions: Optional[List[str]] = None) -> str:
        with self.db:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }

            messages = [{"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"{prompt}"}]

            if not context:
                context = self.context_manager.generate_context(username)
            
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
    def __init__(self, user_full_name: str):
        self.user_name = user_full_name
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

        Note: Always type commands without quotes.
        """)

    def _fetch_recent_logs(self):
        # Fetch the last 25 log messages from the logging module
        for handler in logging.root.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream is log_stream:
                logs = log_stream.getvalue().split('\n')[-25:]
                print('\n'.join(logs))

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
            response_data = self.chat_utility.send_primary_PAI(user_message, self.user_name)

            # If there's an issue with the primary AI or the response is empty, fallback to secondary AI
            if not response_data["response"]:
                logging.info("\nSwitching to secondary AI due to empty response from primary AI.")
                return self.chat_utility.send_secondary_GPT4(user_message, self.user_name)

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
        self.chat_utility.context_manager.add_name_context(self.user_name)
        print("\nWelcome to the Pilot Pro Chat (PROOF OF CONCEPT), Hosted by Ziggy the Personal.ai of Matthew Schafer! \nType 'help' for available commands or 'exit' to exit the chat to the Main Settings Menu.")
        while True:
            try:
                user_message = input(f"\n{self.user_name}: ")

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
