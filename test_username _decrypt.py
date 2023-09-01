# ==========================================
#         test_username_decrypt.py
# ==========================================
#
# Description:
# This module provides utility functions for encrypting and decrypting data using the Fernet encryption scheme.
# It leverages the 'cryptography' library and loads the encryption key from a .env file using the 'dotenv' library.
# 
# Components:
# - ENCRYPTION_KEY: The key used for encryption and decryption.
# - encrypt_data(data: str) -> bytes: Encrypts the provided data.
# - decrypt_data(encrypted_data: bytes) -> str: Decrypts the provided encrypted data.
#
# Usage:
# It's crucial to handle the encryption key securely. Never expose the key in the code or any public repositories.
# Ensure that the .env file containing the encryption key is not pushed to version control systems.
# Use the encrypt_data function to encrypt sensitive information and decrypt_data to retrieve the original data.
#
# Author:
# Matthew Schafer
# Date: Sep 1, 2023
#
# ==========================================

from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the encryption key from the environment variables
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

def encrypt_data(data):
    cipher_suite = Fernet(ENCRYPTION_KEY)
    encrypted_data = cipher_suite.encrypt(data.encode('utf-8'))
    return encrypted_data

def decrypt_data(encrypted_data):
    cipher_suite = Fernet(ENCRYPTION_KEY)
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode('utf-8')
    return decrypted_data

if __name__ == "__main__":
    original_data = "Matthew David Schafer"
    
    encrypted_data = encrypt_data(original_data)
    print(f"Encrypted data: {encrypted_data}")
    
    decrypted_data = decrypt_data(encrypted_data)
    print(f"Decrypted data: {decrypted_data}")
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# End of Encryption Utilities for PilotPro Application.
#
# Note:
# Always ensure the confidentiality and integrity of the encryption key.
# Before deploying the application, review the security measures in place to prevent potential data breaches.
# Ensure the encryption key is backed up securely, as losing it would mean the encrypted data cannot be decrypted.
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
