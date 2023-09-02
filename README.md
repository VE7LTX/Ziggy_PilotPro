# PilotPro Project

The PilotPro project is a comprehensive solution built using Python, designed to interact with various APIs and handle complex data processing tasks. This project is structured to prioritize code maintainability, readability, and modularity, aligning with NASA's standards of programming for spacecraft.

## Contributors

  Matthew Schafer - Lead Software Engineer,
  Marcus Smith - Production Human,
  Cory Canuel - Biology Based Data Science

## Table of Contents

- [PilotPro Project](#pilotpro-project)
  - [Contributors](#contributors)
  - [Table of Contents](#table-of-contents)
  - [Project Structure](#project-structure)
    - [Files](#files)
    - [Modules, Classes, \& Functions](#modules-classes--functions)
      - [`chat_db.py`: Chat Database Management (PilotPro)](#chat_dbpy-chat-database-management-pilotpro)
      - [`chat_utils.py`: Utility Functions for Chat Enhancement](#chat_utilspy-utility-functions-for-chat-enhancement)
      - [`regi.py`: Registration and Encryption Utilities](#regipy-registration-and-encryption-utilities)
      - [Other Files and Modules](#other-files-and-modules)
  - [Setup \& Installation](#setup--installation)
  - [Usage](#usage)
  - [Application User Experience (UX)](#application-user-experience-ux)
  - [Note](#note)
    - [Security](#security)
    - [Maintenance and Updates](#maintenance-and-updates)
    - [Best Practices](#best-practices)

## Project Structure

### Files

- `.env`: Contains configuration data for the PilotPro application. It's used for storing the encryption key required for secure data handling.
- `chat_db.py`: Houses the database functionalities, including establishing a connection, creating tables, and handling CRUD operations.
- `chat_utils.py`: Contains utility functions, especially those related to interacting with the Personal.AI API.
- `constants.py`: Centralized location for defining constant values and configurations used throughout the application.
- `ps.ps1`: PowerShell script used to grab Windows DLLs and copy them to the build folder.
- `regi.py`: A Python script that integrates various functionalities of the project. It acts as a central hub for interactions and data handling.
- `requirements.txt`: Lists all the Python libraries and their versions that are required for this project.
- `template.env`: Template Encryption Key for Main DB Access.
- `template_constants.py_`: Template Constants File, Rename to constants.py.

### Modules, Classes, & Functions

#### `chat_db.py`: Chat Database Management (PilotPro)

This module is central to the PilotPro chat application, handling all SQLite database operations.

- **Description**: The `chat_db.py` manages SQLite database operations for the chat functionalities of PilotPro. It provides interfaces for chat sessions, storage and retrieval of messages, and ensures encryption of chat messages for security.
  
- **Author**: Matthew Schafer
- **Date**: September 2, 2023
- **Company**: VE7LTX Diagonal Thinking LTD

- **Modules & Classes**:
  - **Encryption**:
    - `encrypt`: Encrypts a given message by adding to the ordinal value of each character.
    - `decrypt`: Decrypts an encrypted message by subtracting from the ordinal value of each character.
  - **ChatDatabase Class**:
    - Manages SQLite database connections.
    - `__init__`: Initializes database configurations and sets up the default folder for the database.
    - `open_connection`: Establishes a connection to the SQLite database.
    - `close_connection`: Closes the active database connection.
    - `_create_tables`: Creates the required tables in the SQLite database if they don't exist.
    - `insert_message`: Inserts a new chat message into the database.
    - `get_messages`: Fetches all messages associated with a particular username.
    - `get_last_n_messages`: Retrieves the last 'n' messages for a given username.
    - `close`: Closes the database connection, ensuring data integrity.

- **Usage**:
  1. Install the required packages mentioned in the header.
  2. Instantiate the ChatDatabase class.
  3. Utilize its methods to manage chat sessions and messages.
  4. Ensure closing the database connection after operations.

- **Noteworthy Features**:
  - **Message Encryption**: Every message stored in the database is encrypted for security.
  - **Context Management**: The class is designed to be used with Python's `with` statement for automatic database connection management.
  - **Logging**: Granular logging is available for debugging and tracing, especially useful during development.

- **Security Note**: The current encryption method is basic. For production-level applications or sensitive data, consider integrating more advanced encryption libraries and practices.

- **Performance**: This module is optimized for small to medium-sized applications. For large-scale use or heavy concurrent loads, consider further optimizations or more robust database systems.

- **Future Enhancements**:
  1. Consider more advanced encryption techniques.
  2. Implement database indexing for faster retrieval.
  3. Add a backup mechanism for the database.

- **Feedback & Contributions**: Feedback and contributions are always welcome. Please adhere to the coding standards mentioned in the module's header for consistency.

- **Disclaimer**: The module is provided as-is, and while extensive efforts ensure reliability, no responsibility for any issues or damages arising from its use is taken.

#### `chat_utils.py`: Utility Functions for Chat Enhancement

This module focuses on utility functions, particularly those associated with the interaction between users and two AI models: Personal.AI as the primary AI and GPT-4 as a backup. It emphasizes the dynamic generation of chat context to produce more tailored responses based on prior interactions.

- **Description**: The `chat_utils.py` module offers a suite of tools designed to enhance and streamline chat sessions between users and two AI models: Personal.AI and GPT-4. The module places emphasis on maintaining a dynamic chat context to offer more tailored responses based on previous interactions.

- **Class: `ContextManager`**:
  - **Purpose**: Orchestrates the dynamic generation of context for the AI by leveraging recent chat interactions and other relevant information.
  - **Methods**:
    - `generate_context`: Generates context based on the last 10 message pairs in history and any custom context.
    - `add_custom_context`: Adds custom context to the existing context.
    - `add_name_context`: Adds the user's name to the context.
    - `add_current_time_context`: Adds the current time to the context.
    - `add_last_session_time_context`: Adds the time of the last session to the context.
    - `add_last_message_context`: Adds the last message sent and received to the context.
    - `add_last_n_messages_context`: Adds the last 'n' messages to the context.
    - `add_last_session_messages_context`: Adds the last two message pairs from the last session to the context.

- **Class: `ChatUtility`**:
  - **Purpose**: Facilitates chat communication between the user and both AI models (Personal.AI and GPT-4).
  - **Methods**:
    - `send_primary_PAI`: Sends a message to the Personal.AI API and retrieves the response.
    - `send_secondary_GPT4`: Sends a message to the GPT-4 API and retrieves the response.

- **Class: `ChatSession`**:
  - **Purpose**: Manages individual chat sessions, processes user commands, and integrates AI functionalities.
  - **Methods**:
    - `_show_help`: Displays help information for available commands.
    - `_fetch_recent_logs`: Fetches the last 25 debugging log items.
    - `_exit_session`: Safely terminates the current chat session.
    - `_process_command`: Processes user commands and executes corresponding functions.
    - `_get_response`: Gets AI responses based on user input.
    - `start`: Initiates and manages the chat session loop.

- **Usage**:
  1. Instantiate the `ChatSession` class with the user's full name.
  2. Utilize the `start` method to begin the chat session.
  3. Input text messages to engage in a conversation with the AI models.
  4. Use the available commands ('help', 'logs', 'exit') for enhanced user experience.

- **Noteworthy Features**:
  - Adaptable context generation to leverage recent chat interactions.
  - Capability to add custom context details like the user's name and current time.
  - Dual AI integration: Primary (Personal.AI) and Secondary (GPT-4) for redundancy.
  - Comprehensive logging system for effective debugging.
  - In-session user commands ('help', 'logs', 'exit') for enhanced user experience.

- **Workflow**:
  1. Initiate the chat session with the user's identification.
  2. Incorporate the user's name into the chat context.
  3. Process user input:
     a. Handle in-session commands.
     b. Direct chat inputs to the primary AI.
     c. Utilize the secondary AI in case of primary AI failure or inadequate response.
  4. Display AI responses to the user.
  5. Repeat until the session is terminated by the user.

- **Dependencies**:
  - `requests`: To manage API requests.
  - `logging`: For effective debugging and error tracking.
  - `chat_db`: For database operations and fetching recent chat messages.
  - `constants`: Contains critical constant values like API endpoints and headers.

- **Author**: Matthew Schafer
- **Date**: September 2, 2023
- **Company**: VE7LTX Diagonal Thinking LTD

#### `regi.py`: Registration and Encryption Utilities

This module handles user registration, authentication, session management, and encryption.

- **Description**: The `regi.py` module provides a suite of tools designed to handle user registration, authentication, session management, and encryption. It includes functionalities such as user registration, password change, user role modification, user addition by an admin, user deletion, and initiating a chat session.

- **Class: `CryptoHandler`**:
  - **Purpose**: Handle the generation, encryption, and decryption of user keys and details.
  - **Methods**:
    - `generate_user_key`: Generates a new encryption key for a user.
    - `encrypt_user_key`: Encrypts a user-specific key using the main encryption key.
    - `decrypt_user_key`: Decrypts a user-specific key using the main encryption key.
    - `encrypt_detail_with_key`: Encrypts a detail (like a name) using a user-specific key.
    - `decrypt_detail_with_key`: Decrypts an encrypted detail using a user-specific key.

- **Class: `SessionManager`**:
  - **Purpose**: Handle user session management.
  - **Methods**:
    - `create_session`: Creates a new session for a user.
    - `create_sessions_table`: Creates the sessions table in the database if it doesn't already exist.
    - `validate_session`: Validates a session and returns a tuple of (is_valid, role).
    - `terminate_session`: Deletes a session from the database.

- **Class: `UserManager`**:
  - **Purpose**: Manage user registration, authentication, role management, and user deletion.
  - **Methods**:
    - `register_user`: Registers a new user with the given details.
    - `authenticate_user`: Authenticates a user and returns their full name and role if successful.
    - `set_user_role`: Sets the role of a user.
    - `delete_user`: Performs a clean delete of a user and all related database items.
    - `reset_password`: Resets the password for a user.
    - `add_user_by_admin`: Admin adds a new user with a default password.

- **Class: `App`**:
  - **Purpose**: Manage the main application, user interactions, and orchestrating the functionalities.
  - **Methods**:
    - `main_menu`: Displays the main menu of the application and handles user choices.
    - `handle_choice`: Handles the user's choice from the main menu.
    - `login`: Handles user login.
    - `change_password`: Allows the user to change their password.
    - `modify_user_role`: Allows an admin to modify a user's role.
    - `admin_add_user`: Allows an admin to add a new user.
    - `register`: Handles user registration.
    - `delete_user`: Allows an admin to delete a user.
    - `logout`: Logs out the current user.
    - `exit_app`: Exits the application.
    - `start_chat`: Initiates a chat session for the user.

- **Usage**:
  1. Instantiate the `App` class.
  2. Call the `main_menu` method to start the application.
  3. Follow the prompts to register, login, or exit.
  4. Once logged in, follow the prompts to start a chat, modify user roles, add a user, change password, or logout.

- **Noteworthy Features**:
  - User registration with encryption of sensitive details.
  - User authentication with decryption of encrypted details.
  - Session management with session creation, validation, and termination.
  - User management with role modification, user addition by admin, user deletion, and password reset.
  - Main application management with a main menu, handling user choices, and initiating chat sessions.

- **Dependencies**:
  - `sqlite3`: For database operations.
  - `bcrypt`: For password hashing.
  - `logging`: For effective debugging and error tracking.

- **Author**: Matthew Schafer
- **Date**: September 2, 2023
- **Company**: VE7LTX Diagonal Thinking LTD

#### Other Files and Modules
The project contains several other important files, classes, and functions that are crucial for its functionality:

- **DB**: This folder contains the databases used in the project.
  - `chat.db`: Database containing chat-related data.
  - `users.db`: Database containing user-related data.

- **venv**: This folder contains the virtual environment for the project.

- **.env**: This file contains environment variables required for the project.

- **.gitignore**: This file specifies the files and directories that should be ignored by Git.

- **chat_db.py**: This file contains classes and functions for managing the chat database. For more details, refer to the chat_db.py section.

- **chat_utils.py**: This file contains utility functions for chat enhancement. For more details, refer to the chat_utils.py section.

- **constants.py**: This file contains the constant values used throughout the project.

- **filetree.py**: This file contains the code for generating the file tree of the project.

- **next steps.ipynb**: This Jupyter notebook contains the next steps and plans for the project.

- **ps.ps1**: This PowerShell script contains utility functions for the project.

- **README.md**: This file contains the documentation of the project.

- **regi.py**: This file contains classes and functions for user authentication and chat application. For more details, refer to the regi.py section.

- **requirements.txt**: This file contains the list of packages required to run the project.

- **send_message_to_pai.py**: This file contains the code for sending messages to Personal.AI.

- **template_constants.py**: This file contains the template for the constants.py file.

- **template.env**: This file contains the template for the .env file.

- **test_username_decrypt.py**: This file contains the code for testing username decryption.

## Setup & Installation

1. Prerequisite: Ensure you have Python installed on your machine. This project is developed using Python, so it's crucial to have it installed. You can download the latest version of Python from the official Python website.

2. Clone the Repository: Use the following command to clone the PilotPro repository to your local machine:

```bash
git clone `https://github.com/VE7LTX/Ziggy_PilotPro.git`
```

3. Navigate to the Project Directory: After cloning, you need to navigate into the project's root directory. Use the command:

```bash
cd PilotPro
```

4. Install Required Dependencies: The project requires several Python libraries to function correctly. Install these using the provided requirements.txt file with the following command:

```bash
pip install -r requirements.txt
```

5. Configuring Environment Variables:

    The project utilizes a .env file to manage essential configurations, such as the encryption key.
    If you haven't already, ensure that you create a .env file in the project's root directory. You can use template.env as a template.
    Open the .env file in a text editor and configure the necessary parameters, especially the encryption key.

6. Rename Template Files:

    The project provides template files to guide your setup.
    Rename template.env to .env.
    Rename template_constants.py_ to constants.py.
    Ensure to adjust the contents of these files to match your project's specifics.

7. Final Checks:

    Before running the project, double-check all configurations to ensure accuracy.
    Remember to never commit sensitive information like encryption keys or API keys to public repositories.

8. Running the Application:
    With all dependencies installed and configurations in place, you're now set to run the project. Use the appropriate script or command based on your requirements.

## Usage

1. **Running the Main Script**:
   To start the application, use the following command:

```bash
    python regi.py
```

2. This will initiate the main functionalities and provide prompts for user interactions.

    Interacting with Personal.AI:
    The chat_utils.py module contains functions designed to interact with Personal.AI. This module simplifies the process of sending and receiving messages, ensuring seamless communication with the AI.

```python

    from chat_utils import ChatUtility

    chat_util = ChatUtility()
    response = chat_util.send_message("Hello, Personal.AI!")
```

3. Handling Windows DLLs:
If you need to manage specific Windows DLLs or integrate them into the build folder, utilize the provided PowerShell script:

```bash

    ./ps.ps1
```

## Application User Experience (UX)

PilotPro has been designed with user experience at its core. Here are some highlights.
```
  Intuitive Prompts: Throughout the application, users are provided with clear and concise prompts, guiding them through various functionalities.

  Error Handling: The application is equipped with robust error handling, ensuring that users receive clear feedback on any issues and guidance on how to resolve them.

  Seamless Integration with Personal.AI: The in-built functionalities make the process of communicating with Personal.AI straightforward, enhancing user engagement.

  Customizable Settings: Users have the flexibility to tweak settings and configurations, tailoring the application to their specific needs.

  Help & Documentation: The application provides in-built help commands and extensive documentation, ensuring users always have the information they need at their fingertips.
```

Remember, the key to an exceptional user experience is continuous feedback and iteration. As you interact with PilotPro, any feedback or suggestions for improvement are highly appreciated!

## Note

### Security

- **Sensitive Information**: Always be cautious with sensitive data. The `.env` file, in particular, contains configuration data and encryption keys that are crucial for the secure functioning of the PilotPro application.
  
  - Never commit or push the `.env` file to public repositories.
  - It's a good practice to add `.env` to your `.gitignore` file to prevent accidental commits.
  - Periodically rotate and update keys and other sensitive data to enhance security.

- **Code Review**: Regularly review your codebase for potential security vulnerabilities. Implementing code reviews with peers or automated tools can help in identifying and rectifying potential threats.

- **Database Backups**: Ensure you have a robust backup system in place for your database. This not only prevents data loss but also allows for data recovery in case of breaches or failures.

### Maintenance and Updates

- **Dependencies**: Regularly update the dependencies of your project. Using outdated libraries can introduce vulnerabilities. Always check for updates and ensure they don't introduce new issues in your project.

- **Feedback Loop**: Encourage users to report bugs, issues, or potential security threats. A continuous feedback loop ensures the application remains robust and user-centric.

- **Documentation**: Keep your documentation updated. As you enhance and evolve your application, make sure your documentation reflects those changes, guiding users effectively.

### Best Practices

- **Version Control**: Use version control systems like Git to track changes, maintain history, and facilitate collaboration. It also provides an avenue to rollback changes in case of issues.

- **Environment Isolation**: It's a good practice to have separate environments (development, staging, production) to test changes, ensuring that the production environment remains stable.
