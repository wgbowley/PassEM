"""
File: database.py
Author: William Bowley
Version: 1.0
Date: 2025-08-08

Description:
    Module for reading and writing to the json database file
"""

import json


def read(dbpath: str) -> dict:
    """
    Reads the database file and returns its contents as a dictionary.
    """
    with open(dbpath, "r", encoding="utf-8") as db_file:
        return json.loads(db_file.read())


def write(dbpath: str, data: dict) -> None:
    """
    Writes data to the database file.
    """
    with open(dbpath, 'w', encoding="utf-8") as db_file:
        db_file.write(json.dumps(data))
