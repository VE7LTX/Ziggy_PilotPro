# ==========================================
#               constants.py
# ==========================================
#
# Description:
# This file contains constant values and configurations that are used throughout the application.
# The constants defined in this file are primarily related to API interactions, including Personal.AI 
# and OpenAI API configurations.
#
# Constants:
# - PAI_API_KEY: The API key required to authenticate and interact with the Personal.AI API.
# - BASE_URL: The base endpoint URL for the Personal.AI API.
# - FILE_NAME: Name of the primary file used to log chat data.
# - OPENAI_API_KEY: The API key required to authenticate and interact with the OpenAI API.
# - OPENAI_ENDPOINT: The specific endpoint URL for OpenAI chat completions.
#
# Additionally, there is a headers dictionary (HEADERS) defined, which is pre-configured with
# the necessary headers for making API calls, including the 'Content-Type' and the 'x-api-key'.
# The 'x-api-key' in the headers dictionary is a placeholder which should be replaced with the 
# actual API key when making API calls.
#
# Usage:
# Import the required constants from this file wherever they are needed in the application. Ensure 
# to handle them securely, especially the API keys.
#
# Author: Matthew Schafer
# Date: August 31, 2023
# Company: VE7LTX Diagonal Thinking LTD
#
# ==========================================

# Constants for Personal.AI API
PAI_API_KEY = "Your Personal.ai API Key Here"
BASE_URL = "https://api.personal.ai/v1"

FILE_NAME = "chat_data.jsonl" #main file chat log
BASE_URL = "https://api.personal.ai/v1"
OPENAI_API_KEY = "sk-Your OPENAI Key Here"  # Replace with your actual OpenAI API key
OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"  # Updated to use the completions endpoint

# Define headers with placeholders for the API key
HEADERS = {
    'Content-Type': 'application/json',
    'x-api-key': PAI_API_KEY  # Placeholder, replace with actual key when calling
}

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# End of `constants.py` module.
#
# Overview:
# - The `constants.py` module serves as a centralized location for managing critical constant values.
# - These constants primarily pertain to API configurations and interactions, such as API keys and endpoint URLs.
# - Proper management of these constants is crucial for the secure and effective functioning of the application.
#
# Notes for Future Maintenance:
# - Regularly review and update API keys and endpoints as required.
# - Always treat API keys as sensitive information. Consider implementing enhanced security measures, such as environment variables or secret management tools.
# - When updating or adding new constants, ensure that they are thoroughly documented for clarity.
# - Periodically check for deprecated or outdated API endpoints and update as necessary.
# - If the application scales or if more integrations are added, consider organizing constants into categories or separate files for better maintainability.
#
# Remember: The integrity of the application largely depends on the proper management and security of these constants. Always prioritize security and clarity.
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
