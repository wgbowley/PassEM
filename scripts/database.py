import json

def read(dbpath: str) -> dict:
    """
    Reads the database file and returns its contents as a dictionary.
    """
    with open(dbpath, 'r') as db_file:
        return json.loads(db_file.read())

def write(dbpath: str, data: dict) -> None:
    """
    Writes data to the database file.
    """
    with open(dbpath, 'w') as db_file:
        db_file.write(json.dumps(data))

