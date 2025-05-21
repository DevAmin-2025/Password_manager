# Password_manager
A secure password management system using `SQLite` and `Fernet encryption`, designed to store and manage user credentials for various services.

## Features
- User registration with encrypted password storage.
- Secure authentication for accessing stored credentials.
- Strong password generation for enhanced security.
- Adding and managing passwords for various services.
- Changing stored passwords and usernames.
- Viewing stored credentials with decryption.
- Secure deletion of password entries.

## Project Structure
```
src/
│── password_manager.py   # Core password manager logic
│── main.py               # Entry point and user interaction
│── encryption_key.key    # Generated upon first run
│── data/                 # Created dynamically, contains database file
```

## Installation & Setup
1. **Clone the Repository**: Open your terminal and run the following command to clone the repository:
    ```bash
    git clone https://github.com/your-username/your-repo.git
    ```
    Replace your-username and your-repo with the actual GitHub username and repository name.

2. Navigate to the main project directory and add it to `PYTHONPATH`:
    ```bash
    export PYTHONPATH=$(pwd)
    ```

3. Install any dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the `main.py` script:
    ```bash
    python src/main.py
    ```

## Usage
Upon running the application, you'll see an interactive menu where you can:

- Register a new user (Option 1)
- Change your login password (Option 2)
- Add a password for a service (Option 3)
- Modify stored passwords & usernames (Options 4 & 5)
- View stored credentials (Option 6)
- Delete passwords (Option 7)
- Exit the application (Option 8)

## Security Measures
- Uses `Fernet encryption` to secure stored passwords.
- Protects user credentials in an `SQLite database`.
- Ensures data integrity and access control.

## License
This project is licensed under MIT License—use it responsibly.
