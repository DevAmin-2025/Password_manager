import os
import secrets
import string
from getpass import getpass
from cryptography.fernet import Fernet
import sqlite3

if not os.path.exists("encryption_key.key"):
    encryption_key = Fernet.generate_key()
    with open("encryption_key.key", "wb") as f:
        f.write(encryption_key)

with open("encryption_key.key", "rb") as f:
    encryption_key = f.read()

cipher = Fernet(encryption_key)

os.makedirs("data", exist_ok=True)
conn = sqlite3.connect("data/password_manager.db")
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

def generate_strong_password(length=12):
    char = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(char) for _ in range(length))


def register_user():
    name = input("Please enter your name: ")
    password = getpass("Please set your password (leave blank to generate strong password): ")
    if not password.split():
        password = generate_strong_password()
    encrypted_password = cipher.encrypt(password.encode()).decode()
    try:
        cursor.execute(
            "INSERT INTO users (name, password) VALUES (?, ?)",
            (name, encrypted_password)
            )
        conn.commit()
        print("User registration successful.")
        print(f"Your password is: {password} Please save this password securely.")
    except sqlite3.IntegrityError:
        print("Error: Username already exists! Please choose a different username.")


def login():
    name = input("Please enter your name: ")
    password = getpass("Please enter your password: ")
    cursor.execute(
        "SELECT * FROM users WHERE name = ?",
        (name,)
    )
    user = cursor.fetchone()
    if user:
        decrypted_password = cipher.decrypt(user[2].encode()).decode()
        if decrypted_password == password:
            return name
        else:
            print("Wrong password. Please try again.")
            return False
    else:
        print("User does not exist. You must register first.")
        return False


def change_password():
    name = login()
    if not name:
        return
    new_password = getpass("Please set your new password (leave blank to generate strong password): ")
    if not new_password.split():
        new_password = generate_strong_password()
    encrypted_password = cipher.encrypt(new_password.encode()).decode()
    cursor.execute(
        "UPDATE users set password = ? WHERE name = ?",
        (encrypted_password, name)
    )
    conn.commit()
    print(f"Your new password is: {new_password} Please save this password securely.")


def get_user_id(name):
    cursor.execute(
            "SELECT user_id FROM users WHERE name = ?",
            (name,)
        )
    user = cursor.fetchone()
    user_id = user[0]
    return user_id


def add_password():
    name = login()
    if not name:
        return
    user_id = get_user_id(name)
    website = input("Please enter the name of the website/service: ")
    username = input("Please enter your username for this website/service: ")
    password = getpass("Please enter the password (leave blank to generate strong password): ")
    if not password.split():
        password = generate_strong_password()
    encrypted_password = cipher.encrypt(password.encode()).decode()
    cursor.execute(
        "INSERT INTO passwords (user_id, website, username, password) VALUES (?, ?, ?, ?)",
        (user_id, website, username, encrypted_password)
    )
    conn.commit()
    print("Password successfully added.")


def change_website_password():
    name = login()
    if not name:
        return
    user_id = get_user_id(name)
    website = input("Please enter the name of the website/service you want to change its password: ")
    new_password = getpass("Please set your new password (leave blank to generate strong password): ")
    if not new_password.split():
        new_password = generate_strong_password()
    encrypted_password = cipher.encrypt(new_password.encode()).decode()
    cursor.execute(
        "SELECT website FROM passwords WHERE user_id = ?",
        (user_id,)
    )
    websites = cursor.fetchall()
    website_exists = [website in [w[0] for w in websites]][0]
    if website_exists:
        cursor.execute(
            "UPDATE passwords set password = ? WHERE user_id = ? and website = ?",
            (encrypted_password, user_id, website)
        )
        conn.commit()
        print(f"Password successfully changed for {website}.")
    else:
        print('No such website/service.')


def show_passwords():
    name = login()
    if not name:
        return
    user_id = get_user_id(name)
    cursor.execute(
        "SELECT * FROM passwords WHERE user_id = ?",
        (user_id,)
    )
    passwords = cursor.fetchall()
    for password in passwords:
        decrypted_password = cipher.decrypt(password[4].encode()).decode()
        print(
            f"ID: {password[0]} - User_id: {password[1]} - Website/Service: {password[2]} - Username: {password[3]} - Password: {decrypted_password}"
            )


def delete_password():
    name = login()
    if not name:
        return
    user_id = get_user_id(name)
    try:
        password_id = int(input(
            "Please enter the ID of the password you want to delete. (You can see the IDs by chooing option 5 in the main menu): "
            ))
    except ValueError:
        print("Invalic ID. ID must be an integer.")
        return
    cursor.execute(
        "SELECT id FROM passwords WHERE user_id = ?",
        (user_id,)
    )
    IDs = cursor.fetchall()
    ID_exists = [password_id in [p[0] for p in IDs]][0]
    if ID_exists:
        cursor.execute(
            "DELETE FROM passwords WHERE user_id = ? AND id = ?",
            (user_id, password_id)
        )
        conn.commit()
        print("Deletion successful.")
    else:
        print("There is no password with the given ID.")

while True:
    print("\nPassword Manager:")
    print("\t1. Register")
    print("\t2. Change User-Password")
    print("\t3. Add Password")
    print("\t4. Change Website-Password")
    print("\t5. View Passwords")
    print("\t6. Delete Password")
    print("\t7. Exit")

    choice = input("Select an option: ")
    if choice == "1":
        register_user()
    elif choice == "2":
        change_password()
    elif choice == "3":
        add_password()
    elif choice == "4":
        change_website_password()
    elif choice == "5":
        show_passwords()
    elif choice == "6":
        delete_password()
    elif choice == "7":
        print("Exiting the app...")
        break
    else:
        print("Invalid Input")

conn.close()
