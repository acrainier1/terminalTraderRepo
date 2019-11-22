import sqlite3
import time  # time.time() => floating point unix time stamp for right now
import requests
import os
from .config import DBPATH
from . import account
from . import position
from . import errs

DICT_FAKES = {"STOK": 123.45, "P2P": 678.90, "A33A": 98.76}

def get_current_price(ticker):
    """ return the current price of a given ticker. 
    can raise NoSuchTickerError or ConnectionError """
    if ticker in DICT_FAKES:
        return DICT_FAKES[ticker]

    CRED_DIR = os.path.join( os.getenv('HOME'), ".credentials" )
    IEX_TOKEN = "IEXTOKEN.txt"
    TOKENFILE = os.path.join(CRED_DIR, IEX_TOKEN)
    token = open(TOKENFILE).read().strip()
    api_url = "https://cloud.iexapis.com/stable/stock/{ticker}/quote?token={token}"
    get_url = api_url.format(ticker=ticker, token=token)

    response = requests.get(get_url)
    ticker_symbol = None
    if response.status_code == 200:
        ticker_symbol = response.json()['latestPrice']
        return ticker_symbol
    return ticker_symbol


class Trade:

    dbpath = DBPATH

    @classmethod
    def setDB(cls, dbpath):
        cls.dbpath = dbpath

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.ticker = kwargs.get('ticker')
        self.volume = kwargs.get('volume', 0.0)
        self.unit_price = kwargs.get('unit_price')
        self.time = time.time()
        self.account_id = kwargs.get('account_id')


    def save(self):
        """ inserts or updates depending on id's value """
        if self.id is None:
            self._insert()
        else:
            self._update()


    def _insert(self):
        """ inserts a new row into the database and sets self.id """
        with sqlite3.connect(self.dbpath) as connection:
            cursor = connection.cursor()
            INSERTSQL = """INSERT INTO trades
(ticker, volume, unit_price, time, account_id) VALUES 
(:ticker, :volume, :unit_price, :time, :account_id);"""
            values = {
                    "ticker": self.ticker,
                    "volume": self.volume,
                    "unit_price": self.unit_price,
                    "time": self.time,
                    "account_id": self.account_id 
                    }
            try:
                cursor.execute(INSERTSQL, values)
                self.id = cursor.lastrowid
            except sqlite3.IntegrityError:
                raise ValueError("Ticker not set or is not found") # UNIQUE(4.cker, account_id)


    def _update(self):
        """ updates the row with id=self.id with this objects current values"""
        with sqlite3.connect(self.dbpath) as connection:
            cursor = connection.cursor()
            UPDATESQL = """UPDATE trades
SET ticker=:ticker, volume=:volume, unit_price=:unit_price, time=:time, account_id=:account_id
WHERE id=:id;"""
            values = {
                    "ticker": self.ticker,
                    "volume": self.volume,
                    "unit_price": self.unit_price,
                    "time": self.time,
                    "account_id": self.account_id,
                    "id": self.id
                    }
            try:
                cursor.execute(UPDATESQL, values)
            except sqlite3.IntegrityError:
                raise ValueError("ID (id) does not set in datebase.")


    def delete(self):
        """ deletes row with id=self.id from db and sets self.id to None """
        with sqlite3.connect(self.dbpath) as connection:
            cursor = connection.cursor()
            DELETESQL = """DELETE FROM trades WHERE id=:id;"""
            values = {
                    "id": self.id
                    }
            cursor.execute(DELETESQL, values)
            # try:
            #     cursor.execute(DELETESQL, values)
            # except sqlite3.IntegrityError: # as E
            #     raise ValueError("ID does not exist in datebase.")


    @classmethod
    def from_id(cls, id):
        """ return an object of this class for the given database row id """
        SELECTSQL = "SELECT * FROM trades WHERE id=:id;"
        with sqlite3.connect(cls.dbpath) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(SELECTSQL, {"id": id})
            dictrow = cursor.fetchone()
            if dictrow:
                return cls(**dictrow)
            return None


    @classmethod
    def all(cls):
        """ return a list of every row of this table as objects of this class """
        with sqlite3.connect(cls.dbpath) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            SQL = "SELECT * FROM trades;"
            cursor.execute(SQL)
            result = []
            for dictrow in cursor.fetchall():
                result.append(cls(**dictrow))
            return result
            

    @classmethod
    def delete_all(cls):
        with sqlite3.connect(cls.dbpath) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            SQL = "DELETE FROM trades;"
            cursor.execute(SQL)
            result = []
            for dictrow in cursor.fetchall():
                result.append(cls(**dictrow))
            return result


    @classmethod
    def all_from_account_id(cls, account_id):
        """ return a list of Trade objects for all of a given account's trades """
        with sqlite3.connect(cls.dbpath) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            SQL = "SELECT * FROM trades WHERE account_id=:account_id;"
            cursor.execute(SQL, {"account_id": account_id})
            result = []
            for dictrow in cursor.fetchall():
                result.append(cls(**dictrow))
            return result


    @classmethod
    def all_from_account_id_and_ticker(cls, account_id, ticker):
        """ return a list of Trade object for all of a given accounts trades
        for a given ticker symbol """
        with sqlite3.connect(cls.dbpath) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            SQL = "SELECT * FROM trades WHERE account_id=:account_id AND ticker=:ticker;"
            values = {
                    "account_id": account_id,
                    "ticker": ticker
            }
            cursor.execute(SQL, values)
            result = []
            for dictrow in cursor.fetchall():
                result.append(cls(**dictrow))
            return result


    def get_account(self):
        """ return the Account object for this trade """
        return account.Account.from_id(self.account_id)


    def get_position(self):
        """ return the Position object for this trade """
        return position.Position.from_account_id_and_ticker(self.account_id, self.ticker)


    def __repr__(self):
        """ return a string representing this object """
        # this is a good default __repr__
        return f"<{type(self).__name__} {self.__dict__}>"
