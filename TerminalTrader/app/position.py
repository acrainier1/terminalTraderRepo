import sqlite3
from .config import DBPATH
from . import account
from . import trade
from . import errs
# """
# CREATE TABLE positions(
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         ticker VARCHAR(15) NOT NULL,
#         shares FLOAT,
#         account_id INTEGER,
#         FOREIGN KEY ("account_id") REFERENCES account(id)
#         UNIQUE(ticker, account_id)
#     );
# """

class Position:

    dbpath = DBPATH

    @classmethod
    def setDB(cls, dbpath):
        cls.dbpath = dbpath


    def __init__(self, **kwargs):
        """ sets each field from kwargs """
        self.id = kwargs.get("id")
        self.ticker = kwargs.get("ticker")
        self.shares = kwargs.get("shares", 0)
        self.account_id = kwargs.get("account_id")


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
            INSERTSQL = """INSERT INTO positions(ticker, shares, account_id) 
            VALUES (:ticker, :shares, :account_id); """
            values = {
                "ticker": self.ticker,
                "shares" : self.shares, 
                "account_id" : self.account_id 
            }
            try: 
                cursor.execute(INSERTSQL, values)
                self.id = cursor.lastrowid      
            except sqlite3.IntegrityError:
                raise ValueError("ticker not set or a position for this ticker already exists")


    def _update(self):
        """ updates the row with id=self.id with this objects current values"""
        with sqlite3.connect(self.dbpath) as connection: 
            cursor = connection.cursor()
            UPDATESQL = """UPDATE positions 
            SET ticker=:ticker, shares=:shares, account_id=:account_id 
            WHERE id=:id;"""
            values = {
                "ticker": self.ticker,
                "shares" : self.shares, 
                "account_id" : self.account_id,
                "id" : self.id
                }
            try:
                cursor.execute(UPDATESQL, values)
                # Check back on this line here..... do we need to raise an error?
            except sqlite3.IntegrityError:
                raise ValueError("ticker not set or a position for this ticker already exists")


    def delete(self):
        """ deletes row with id=self.id from db and sets self.id to None """
        with sqlite3.connect(self.dbpath) as connection: 
            cursor = connection.cursor()
            DELETESQL = "DELETE FROM positions WHERE id=:id;"
            try: 
                cursor.execute(DELETESQL, {"id" : self.id})
                self.id = None
            except sqlite3.IntegrityError: ## dont think an error actually appears here -- how do we account for this?
                raise ValueError("id does not exist")
        

    @classmethod
    def delete_all(cls):
        """ delete all rows from this table """
        with sqlite3.connect(cls.dbpath) as connection:
            cursor = connection.cursor()
            DELETE_SQL = "DELETE FROM positions;"
            cursor.execute(DELETE_SQL)
            

    @classmethod
    def from_id(cls, id):
        """ return an object of this class for the given database row id """
        with sqlite3.connect(cls.dbpath) as connection:
            SELECTSQL = "SELECT * FROM positions WHERE id=:id;"
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(SELECTSQL, {"id": id})
            dictrow = cursor.fetchone()
            if dictrow:
                # this is creating an instance with that particular row of data
                return cls(**dictrow)
            return None

    @classmethod
    def all(cls):
        """ return a list of every row of this table as objects of this class """
        with sqlite3.connect(cls.dbpath) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            SELECTSQL = "SELECT * FROM positions;"
            cursor.execute(SELECTSQL)
            result = []
            for dictrow in cursor.fetchall():
                result.append(cls(**dictrow))
            return result


    def __repr__(self):
        """ return a string representing this object """
        # this is a good default __repr__
        return f"<{type(self).__name__} {self.__dict__}>"
    
    def value(self):
        """ look up the current price and return that * number of shares """
        ## will complete w API integration
        pass


    @classmethod
    def all_from_account_id(cls, account_id):
        """ return every Position object for a given account_id that has more than
        0 shares """
        with sqlite3.connect(cls.dbpath) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            SELECTSQL = "SELECT * FROM positions WHERE account_id=:account_id AND shares>0;"
            cursor.execute(SELECTSQL, {"account_id": account_id})
            result = []
            for dictrow in cursor.fetchall():
                result.append(cls(**dictrow))
            return result


    @classmethod
    def from_account_id_and_ticker(cls, account_id, ticker):
        """ return the Position object for a given account_id and ticker symbol
        if there is no such position, return a new object with zero shares """
        with sqlite3.connect(cls.dbpath) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            SELECTSQL = "SELECT * FROM positions WHERE account_id=:account_id AND ticker=:ticker;"
            values = {
                    "account_id": account_id,
                    "ticker": ticker
                }
            cursor.execute(SELECTSQL, values)
            result = None # result = [] in previous logic, list isn't ideal
            for dictrow in cursor.fetchall():
                result = cls(**dictrow)
            if result is None:
                return cls(account_id=account_id, ticker=ticker, shares=0)
            return result


    def get_account(self):
        """ return the Account object associated with this object """
        return account.Account.from_id(self.account_id)
    

    def get_trades(self):
        """ return the Trades associated with this object """
        return trade.Trade.all_from_account_id_and_ticker(self.account_id, self.ticker)