import sqlite3
from app.config import DBPATH

def schema(dbpath=DBPATH):
    """
    Create these tables

    account:
        id, username, password_hash, balance, first, last

    position:
        id, ticker, shares, account_id

    trade:
        id, ticker, volume, time, price, account_id
    """
    
    # TODO: Put Unique constraints back in.
    
    CREATE_SQL_ACCOUNTS = """
    CREATE TABLE accounts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name VARCHAR(200),
        last_name VARCHAR(200),
        username VARCHAR(15) NOT NULL,
        email_address VARCHAR(50),
        password_hash VARCHAR(30),
        balance FLOAT,
        account_number INTEGER,
        admin INTEGER,
        UNIQUE(account_number)
    ); """

    CREATE_SQL_POSITIONS = """
    CREATE TABLE positions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker VARCHAR(15) NOT NULL,
        shares FLOAT,
        account_id INTEGER,
        FOREIGN KEY ("account_id") REFERENCES accounts(id),
        UNIQUE(ticker, account_id)
    ); """

    
    CREATE_SQL_TRADES = """
    CREATE TABLE trades(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker VARCHAR(5) NOT NULL,
        volume FLOAT,
        unit_price FLOAT,
        time DATE,
        account_id INTEGER,
        FOREIGN KEY ("account_id") REFERENCES accounts(id)
    ); """


    DROPSQL_ACCOUNTS = "DROP TABLE IF EXISTS accounts;"
    DROPSQL_POSITIONS = "DROP TABLE IF EXISTS positions;"
    DROPSQL_TRADES = "DROP TABLE IF EXISTS trades;"


    with sqlite3.connect(dbpath) as conn:
        cursor = conn.cursor()
        cursor.execute(DROPSQL_ACCOUNTS)
        cursor.execute(DROPSQL_POSITIONS)
        cursor.execute(DROPSQL_TRADES)
        cursor.execute(CREATE_SQL_ACCOUNTS)
        cursor.execute(CREATE_SQL_POSITIONS)
        cursor.execute(CREATE_SQL_TRADES)


if __name__ == "__main__":
    schema()