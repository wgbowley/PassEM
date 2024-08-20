import bcrypt
import os
import json
import logging
from scripts import crypt, database
from random import choice
from string import ascii_letters, digits

def generate_salt() -> bytes:
    """
    Generate a new salt using bcrypt.
    """
    salt = bcrypt.gensalt()
    logging.info("Generated new salt.")
    return salt

def hash_password(password: str, salt: bytes) -> str:
    """
    Hash the password with bcrypt using the provided salt.
    """
    hashed_password = bcrypt.hashpw(password.encode(), salt).decode()
    logging.info("Password hashed.")
    return hashed_password

def initialize_db(dbpath: str, password: str) -> None:
    """
    Initialize the database with a hashed password and salt.
    """
    if not os.path.exists(dbpath):
        salt = generate_salt()
        hashed_password = hash_password(password, salt)
        initial_data = {
            "user": {
                "salt": salt.decode(),  # Store salt as a string
                "password": hashed_password
            },
            "accounts": {}
        }
        try:
            database.write(dbpath, initial_data)
            logging.info("Database initialized.")
        except IOError:
            logging.error("Failed to initialize the database.")
            raise

def password_check(dbpath: str, password: str) -> bool:
    """
    Check if the provided password matches the stored hash.
    """
    try:
        db_data = database.read(dbpath)
        salt = db_data['user'].get('salt', '').encode()
        stored_hash = db_data['user'].get('password', '')
        is_valid = bcrypt.checkpw(password.encode(), stored_hash.encode())
        logging.info("Password check performed.")
        return is_valid
    except (IOError, KeyError, TypeError) as e:
        logging.error(f"Password check failed: {e}")
        return False

def load_db(dbpath: str, master_pass: str) -> dict:
    """
    Load and decrypt the database.
    """
    try:
        db_data = database.read(dbpath)
        decrypted_data = {}
        for account_id, encrypted_account in db_data.get('accounts', {}).items():
            decrypted_data[account_id] = crypt.decrypt(encrypted_account, master_pass)
        logging.info("Database loaded and decrypted.")
        return decrypted_data
    except (IOError, KeyError, TypeError) as e:
        logging.error(f"Failed to load database: {e}")
        return {}

def edit_account(dbpath: str, account_id: str, edited_account: dict, master_pass: str) -> None:
    """
    Encrypt and save the edited account details.
    """
    try:
        db_data = database.read(dbpath)
        encrypted_account = crypt.encrypt(json.dumps(edited_account), master_pass)
        db_data['accounts'][account_id] = encrypted_account
        database.write(dbpath, db_data)
        logging.info(f"Account {account_id} edited.")
    except (IOError, KeyError, TypeError) as e:
        logging.error(f"Failed to edit account {account_id}: {e}")

def add_account(dbpath: str, id_length: int, master_pass: str, new_account: dict) -> None:
    """
    Encrypt and add a new account to the database.
    """
    try:
        db_data = database.read(dbpath)
        new_account_id = generate_id(id_length)
        new_encrypted_account = crypt.encrypt(json.dumps(new_account), master_pass)
        db_data['accounts'][new_account_id] = new_encrypted_account
        database.write(dbpath, db_data)
        logging.info(f"Account {new_account_id} added.")
    except (IOError, KeyError, TypeError) as e:
        logging.error(f"Failed to add account: {e}")

def delete_account(dbpath: str, account_id: str) -> None:
    """
    Delete an account from the database.
    """
    try:
        db_data = database.read(dbpath)
        if account_id in db_data['accounts']:
            del db_data['accounts'][account_id]
            database.write(dbpath, db_data)
            logging.info(f"Account {account_id} deleted.")
    except (IOError, KeyError, TypeError) as e:
        logging.error(f"Failed to delete account {account_id}: {e}")

def generate_id(length: int) -> str:
    """
    Generate a random account ID.
    """
    characters = ascii_letters + digits
    account_id = ''.join(choice(characters) for _ in range(length))
    logging.info("Generated a new ID.")
    return account_id
