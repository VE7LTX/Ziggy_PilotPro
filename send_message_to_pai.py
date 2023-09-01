"""
-------------------------------------------------------------------------------
               Send a Message to Personal.AI - Script Description
-------------------------------------------------------------------------------

Purpose:
    Automates the process of sending a message to Personal.AI and receiving a response.
    It displays the AI's message and associated score after processing the input message.

Features:
    - Utilizes the Personal.AI API for message interactions.
    - Retrieves API configurations from 'constants.py'.
    - Displays debug logs for tracking each step of the process.

Usage:
    Run the script using the command:
    $ python send_message_to_pai.py

Example:
    Upon running the script:
    Enter the text to send to your AI: hi

    It will generate logs similar to the following:
    DEBUG: Preparing to send message to Personal.AI
    DEBUG: BASE_URL: https://api.personal.ai/v1
    DEBUG: ETC ETC ETC...

Author Information:
    Name: Matthew Schafer
    Date: August 31, 2023
    Associated Company: VE7LTX Diagonal Thinking LTD

Please ensure you handle all sensitive data, especially API keys, with care and adhere to the Personal.AI API's terms of use.

-------------------------------------------------------------------------------
"""

import requests
import json
from constants import PAI_API_KEY, BASE_URL, HEADERS

def send_message_to_pai(text, domain_name=None):
    print("DEBUG: Preparing to send message to Personal.AI")
    print("DEBUG: BASE_URL:", BASE_URL)
    print("DEBUG: HEADERS:", HEADERS)
    print("DEBUG: Text:", text)
    print("DEBUG: DomainName:", domain_name)
    
    url = f"{BASE_URL}/message"
    payload = {
        "Text": text,
        "DomainName": domain_name,
    }
    print("DEBUG: Payload:", payload)
    
    print("DEBUG: Sending request to Personal.AI")
    response = requests.post(url, headers=HEADERS, json=payload)
    print("DEBUG: Response received:", response.status_code, response.reason)
    
    response_json = response.json()
    print("DEBUG: Response JSON:", response_json)
    
    ai_message = response_json.get('ai_message')
    ai_score = response_json.get('ai_score')
    print("DEBUG: AI Message:", ai_message)
    print("DEBUG: AI Score:", ai_score)
    
    return response_json

if __name__ == "__main__":
    text = input("Enter the text to send to your AI: ")
    domain_name = "ms"
    response = send_message_to_pai(text, domain_name)
    print("DEBUG: Final response:", response)
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# End of the "send_message_to_pai.py" script.
#
# Note:
# This script is designed to facilitate interactions with the Personal.AI platform.
# Ensure that the API key and other sensitive information are handled securely.
# Regularly check the Personal.AI API documentation for any updates or changes that could affect this script's functionality.
# Reach out to the Personal.AI support for any issues or clarifications regarding the API.
#
# VE7LTX Diagonal Thinking LTD retains all rights and responsibilities associated with this script.
# Unauthorized distribution, modification, or misuse is strictly prohibited.
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
