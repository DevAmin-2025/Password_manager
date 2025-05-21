import os
import secrets
import sqlite3
import string
from getpass import getpass
from typing import Union

from cryptography.fernet import Fernet
from termcolor import colored


class PasswordManager:
    """
    A password manager that securely stores user passwords with encryption.

    It provides functionalities for user registration, login, password management and more.

    :param cipher: The Fernet encryption object.
    :param conn: SQLite database connection.
    :param cursor: SQLite cursor for executing queries.
    """
    def __init__(self, cipher, conn, cursor):
        self.cipher = cipher
        self.conn = conn
        self.cursor = cursor

    @staticmethod
    def print_info(text:str):
        """
        Prints informational messages in a styled format.

        :param text: The message to print.
        """
        print(colored(text, 'white', attrs=['reverse']))

    def generate_strong_password(self, length: int = 12) -> str:
        """
        Generates a cryptographically strong random password.

        :param length: The desired length of the password, defaults to 12.
        :return: A randomly generated strong password.
        """
        char = string.ascii_letters + string.digits + string.punctuation
        return "".join(secrets.choice(char) for _ in range(length))

    def register_user(self):
        """
        Registers a new user with an encrypted password.

        Prompts for a username and password, encrypts the password, and saves it in the database.

        :raises sqlite3.IntegrityError: If the username is already taken.
        """
        name = input("Please enter your name: ")
        password = getpass("Please set your password (leave blank to generate strong password): ")
        if not password.split():
            password = self.generate_strong_password()
        encrypted_password = self.cipher.encrypt(password.encode()).decode()
        try:
            self.cursor.execute(
                "INSERT INTO users (name, password) VALUES (?, ?)",
                (name, encrypted_password)
                )
            self.conn.commit()
            self.print_info("\nUser registration successful.")
            self.print_info(f"Your password is: {password} Please save this password securely.")
        except sqlite3.IntegrityError:
            self.print_info("\nError: Username already exists! Please choose a different username.")

    def login(self) -> Union[str, bool]:
        """
        Authenticates a user by checking credentials.

        :return: The username if login is successful, otherwise False.
        """
        name = input("Please enter your name: ")
        password = getpass("Please enter your password: ")
        self.cursor.execute(
            "SELECT * FROM users WHERE name = ?",
            (name,)
        )
        user = self.cursor.fetchone()
        if user:
            decrypted_password = self.cipher.decrypt(user[2].encode()).decode()
            if decrypted_password == password:
                return name
            else:
                self.print_info("\nWrong password. Please try again.")
                return False
        else:
            self.print_info("\nUser does not exist. You must register first.")
            return False

    def change_password(self):
        """
        Allows a user to change their login password securely.

        Prompts the user for a new password and updates the database.
        """
        name = self.login()
        if not name:
            return
        new_password = getpass("Please set your new password (leave blank to generate strong password): ")
        if not new_password.split():
            new_password = self.generate_strong_password()
        encrypted_password = self.cipher.encrypt(new_password.encode()).decode()
        self.cursor.execute(
            "UPDATE users set password = ? WHERE name = ?",
            (encrypted_password, name)
        )
        self.conn.commit()
        self.print_info(f"\nYour new password is: {new_password} Please save this password securely.")

    def get_user_id(self, name: str) -> int:
        """
        Retrieves the user ID based on the username.

        :param name: The name of the user.
        :return: The user's ID.
        """
        self.cursor.execute(
            "SELECT user_id FROM users WHERE name = ?",
            (name,)
            )
        user = cursor.fetchone()
        user_id = user[0]
        return user_id

    def add_password(self):
        """
        Adds a new password for a website/service for the logged-in user.

        Encrypts the password before storing it in the database.
        """
        name = self.login()
        if not name:
            return
        user_id = self.get_user_id(name)
        website = input("Please enter the name of the website/service: ")
        username = input("Please enter your username for this website/service: ")
        password = getpass("Please enter the password (leave blank to generate strong password): ")
        if not password.split():
            password = self.generate_strong_password()
        encrypted_password = self.cipher.encrypt(password.encode()).decode()
        self.cursor.execute(
            "INSERT INTO passwords (user_id, website, username, password) VALUES (?, ?, ?, ?)",
            (user_id, website, username, encrypted_password)
        )
        self.conn.commit()
        self.print_info("\nPassword successfully added.")

    def change_website_password(self):
        """
        Updates the saved password for a specific website/service.

        Prompts the user to log in.
        Checks if the website exists in the database for the user.
        Allows the user to set a new password or generate a strong one.
        Encrypts the new password and updates the database.
        """
        name = self.login()
        if not name:
            return
        user_id = self.get_user_id(name)
        website = input("Please enter the name of the website/service you want to change its password: ")
        new_password = getpass("Please set your new password (leave blank to generate strong password): ")
        if not new_password.split():
            new_password = self.generate_strong_password()
        encrypted_password = self.cipher.encrypt(new_password.encode()).decode()
        self.cursor.execute(
            "SELECT website FROM passwords WHERE user_id = ?",
            (user_id,)
        )
        websites = self.cursor.fetchall()
        website_exists = [website in [w[0] for w in websites]][0]
        if website_exists:
            self.cursor.execute(
                "UPDATE passwords set password = ? WHERE user_id = ? and website = ?",
                (encrypted_password, user_id, website)
            )
            self.conn.commit()
            self.print_info(f"\nPassword successfully changed for '{website}'.")
        else:
            self.print_info("\nNo such website/service.")

    def change_website_username(self):
        """
        Updates the saved username for a specific website/service.

        Prompts the user to log in.
        Checks if the website exists in the database for the user.
        Allows the user to set a new username.
        """
        name = self.login()
        if not name:
            return
        user_id = self.get_user_id(name)
        website = input("Please enter the name of the website/service you want to change its username: ")
        self.cursor.execute(
            "SELECT website FROM passwords WHERE user_id = ?",
            (user_id,)
        )
        websites = self.cursor.fetchall()
        website_exists = [website in [w[0] for w in websites]][0]
        if website_exists:
            new_username = input(f"Please enter your new username for {website}: ")
            self.cursor.execute(
                "UPDATE passwords set username = ? WHERE user_id = ? and website = ?",
                (new_username, user_id, website)
            )
            self.conn.commit()
            self.print_info(f"\nUsername successfully changed for '{website}'.")
        else:
            self.print_info("\nNo such website/service.")

    def show_passwords(self):
        """
        Displays all stored passwords for the logged-in user.

        Retrieves encrypted passwords from the database.
        Decrypts and prints stored credentials in a formatted way.
        Handles empty results by notifying the user.
        """
        name = self.login()
        if not name:
            return
        user_id = self.get_user_id(name)
        self.cursor.execute(
            "SELECT * FROM passwords WHERE user_id = ?",
            (user_id,)
        )
        passwords = cursor.fetchall()
        if passwords:
            for password in passwords:
                decrypted_password = self.cipher.decrypt(password[4].encode()).decode()
                self.print_info(
                    f"ID: {password[0]} - User_id: {password[1]} - Website/Service: {password[2]} - Username: {password[3]} - Password: {decrypted_password}"
                    )
        else:
            self.print_info("You haven't add any passwords yet.")

    def delete_password(self):
        """
        Deletes a saved password entry from the database.

        Prompts the user to log in.
        Lists available password IDs.
        Confirms deletion before removing an entry.

        :raises ValueError: If the entered ID is not a valid integer.
        """
        name = self.login()
        if not name:
            return
        user_id = self.get_user_id(name)
        self.cursor.execute(
            "SELECT id FROM passwords WHERE user_id = ?",
            (user_id,)
        )
        IDs = self.cursor.fetchall()
        if IDs:
            try:
                password_id = int(input(
                    "Please enter the ID of the password you want to delete. (You can see the IDs by chooing option 5 in the main menu): "
                    ))
            except ValueError:
                self.print_info("\nInvalid ID. ID must be an integer.")
                return
            ID_exists = [password_id in [p[0] for p in IDs]][0]
            if ID_exists:
                self.cursor.execute(
                    "DELETE FROM passwords WHERE user_id = ? AND id = ?",
                    (user_id, password_id)
                )
                self.conn.commit()
                self.print_info("\nDeletion successful.")
            else:
                self.print_info("\nThere is no password with the given ID.")
        else:
            self.print_info("You haven't add any passwords yet.")


if __name__ == "__main__":
    if not os.path.exists("src/encryption_key.key"):
        encryption_key = Fernet.generate_key()
        with open("src/encryption_key.key", "wb") as f:
            f.write(encryption_key)
    with open("src/encryption_key.key", "rb") as f:
        encryption_key = f.read()
    cipher = Fernet(encryption_key)

    os.makedirs("src/data", exist_ok=True)
    conn = sqlite3.connect("src/data/password_manager.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            website VARCHAR(50) NOT NULL,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(50) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
    """)
    conn.commit()

    pm = PasswordManager(cipher, conn, cursor)
    while True:
        print("\nPassword Manager:")
        print("\t1. Register")
        print("\t2. Change User-Password")
        print("\t3. Add Password")
        print("\t4. Change Website-Password")
        print("\t5. Change Website-Username")
        print("\t6. View Passwords")
        print("\t7. Delete Password")
        print("\t8. Exit")

        choice = input("Select an option: ")
        if choice == "1":
            pm.register_user()
        elif choice == "2":
            pm.change_password()
        elif choice == "3":
            pm.add_password()
        elif choice == "4":
            pm.change_website_password()
        elif choice == "5":
            pm.change_website_username()
        elif choice == "6":
            pm.show_passwords()
        elif choice == "7":
            pm.delete_password()
        elif choice == "8":
            pm.print_info("\nExiting the app...")
            break
        else:
            pm.print_info("\nInvalid Input")
    conn.close()
