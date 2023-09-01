# PilotPro Project

The PilotPro project is a comprehensive solution built using Python, designed to interact with various APIs and handle complex data processing tasks. This project is structured to prioritize code maintainability, readability, and modularity, aligning with NASA's standards of programming for spacecraft.

## Table of Contents

- [PilotPro Project](#pilotpro-project)
  - [Table of Contents](#table-of-contents)
  - [Project Structure](#project-structure)
    - [Files](#files)
    - [Modules \& Classes](#modules--classes)
  - [Setup \& Installation](#setup--installation)
  - [Usage](#usage)
  - [Contributors](#contributors)
  - [Note](#note)

## Project Structure

### Files

- `.env`: Contains configuration data for the PilotPro application. It's used for storing the encryption key required for secure data handling.
- `chat_db.py`: Houses the database functionalities, including establishing a connection, creating tables, and handling CRUD operations.
- `chat_utils.py`: Contains utility functions, especially those related to interacting with the Personal.AI API.
- `constants.py`: Centralized location for defining constant values and configurations used throughout the application.
- `ps.ps1`: PowerShell script used to grab Windows DLLs and copy them to the build folder.
- `regi.py`: A Python script with an unclear purpose from the given file name, but it seems to have a significant role in the project. (You might want to add more details on this!)
- `requirements.txt`: Lists all the Python libraries and their versions that are required for this project.
- `template.env`: Template Encryption Key for Main DB Access
- `template_constants.py_`: Template Constants File, Rename to constants.py
  
### Modules & Classes

- `chat_db.py`:
  - `ChatDatabase`: Handles SQLite database operations related to chat data.
- `chat_utils.py`:
  - `ChatUtility`: Offers various utility functions, including sending messages to Personal.AI.

## Setup & Installation

1. Ensure you have Python installed on your machine.
2. Clone the `PilotPro` repository to your local machine.
3. Navigate to the project directory.
4. Install the required packages using the command:

   pip install -r requirements.txt

5. Ensure to configure your .env file with the necessary configurations, especially the encryption key.
6. Rename the template files `template.env` to `.env` and `template_constants.py` to `constants.py` and adjust their contents accordingly.

## Usage

For general usage, run the desired Python script:

python `regi.py`

To interact with Personal.AI, you can utilize the functions in `chat_utils.py`.
If you need to grab specific Windows DLLs and copy them to the build folder, you can execute the ps.ps1 PowerShell script.

## Contributors

    Matthew Schafer
    Marcus Smith
    Cory Canuel

## Note

 Ensure to secure your .env file and never commit or push it to public repositories as it contains sensitive information. Always keep backups of your data and periodically review your code for any security vulnerabilities.
