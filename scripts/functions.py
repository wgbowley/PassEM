"""
File: functions.py
Author: William Bowley
Version: 1.0
Date: 2025-08-08

Description:
    Module for helper functions:
    - generate_salt()
    - hash_password()
    - initialize_db()
    - password_check()
    - load_db()
    - edit_account()
    - add_account()
    - delete_account()
    - generate_id()
"""

import os
import json
import logging

from random import choice
from string import ascii_letters, digits

# Third party packages
import bcrypt
from scripts import crypt, database


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
        stored_hash = db_data['user'].get('password', '')
        is_valid = bcrypt.checkpw(password.encode(), stored_hash.encode())
        logging.info("Password check performed.")
        return is_valid
    except (IOError, KeyError, TypeError):
        logging.error("Password check failed", exc_info=True)
        return False


def load_db(dbpath: str, master_pass: str) -> dict:
    """
    Load and decrypt the database.
    """
    try:
        db_data = database.read(dbpath)
        return {
            aid: crypt.decrypt(acc, master_pass)
            for aid, acc in db_data.get('accounts', {}).items()
        }
    except (IOError, KeyError, TypeError) as e:
        logging.error("Failed to load database: %s", e)
        return {}


def edit_account(
    dbpath: str,
    account_id: str,
    edited_account: dict,
    master_pass: str
) -> None:
    """
    Encrypt and save the edited account details.
    """
    try:
        db_data = database.read(dbpath)
        account = crypt.encrypt(json.dumps(edited_account), master_pass)
        db_data['accounts'][account_id] = account
        database.write(dbpath, db_data)
        logging.info("Account %s edited.", account_id)
    except (IOError, KeyError, TypeError):
        logging.error("Failed to edit account %s", account_id, exc_info=True)


def add_account(
    dbpath: str,
    id_length: int,
    master_pass: str,
    new_account: dict
) -> None:
    """
    Encrypt and add a new account to the database.
    """
    try:
        db = database.read(dbpath)
        aid = generate_id(id_length)
        enc = crypt.encrypt(json.dumps(new_account), master_pass)
        db.setdefault('accounts', {})[aid] = enc
        database.write(dbpath, db)
        logging.info("Account %s added.", aid)
    except (IOError, KeyError, TypeError) as e:
        logging.error("Failed to add account: %s", e)


def delete_account(dbpath: str, account_id: str) -> None:
    try:
        db_data = database.read(dbpath)
        if account_id in db_data.get('accounts', {}):
            del db_data['accounts'][account_id]
            database.write(dbpath, db_data)
            logging.info("Account %s deleted.", account_id)
    except (IOError, KeyError, TypeError):
        logging.error("Failed to delete account %s", account_id, exc_info=True)


def generate_id(length: int) -> str:
    """
    Generate a random account ID.
    """
    characters = ascii_letters + digits
    account_id = ''.join(choice(characters) for _ in range(length))
    logging.info("Generated a new ID.")
    return account_id
