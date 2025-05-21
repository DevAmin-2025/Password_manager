import os
import sqlite3

from cryptography.fernet import Fernet

from src.password_manager import PasswordManager

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
