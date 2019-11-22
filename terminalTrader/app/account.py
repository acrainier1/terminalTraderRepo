import sqlite3
import bcrypt
from random import randint
from . import position
from . import trade
from . import errs
from .config import DBPATH

Position = position.Position
Trade = trade.Trade

"""
Circular Imports:

When file A imports B and B imports A, this can cause issues with the from x 
import y method of importing can raise errors. Inside the module we need to
use the position.Position way of naming the class but because of our imports
in __init__.py, code that uses this module does not need to worry about that.

from . import 

. means 'this folder in the module'
"""

class Account:

    dbpath = DBPATH

    @classmethod
    def setDB(cls, dbpath):
        cls.dbpath = dbpath

    def __init__(self, **kwargs):
        """ sets each field from kwargs """
        self.id = kwargs.get("id")
        self.first_name = kwargs.get("first_name")
        self.last_name = kwargs.get("last_name")
        self.username = kwargs.get("username")
        self.email_address = kwargs.get("email_address")
        self.password_hash = kwargs.get("password_hash")
        self.balance = kwargs.get("balance", 0.00)
        self.account_number = kwargs.get("account_number")
        self.admin = kwargs.get("admin", 0)



    def save(self):
        """ inserts or updates depending on id's value """
        if self.id is None:
            self._insert()
        else:
            self._update()


    def _insert(self):
        """ inserts a new row into the database and sets self.id """
        self.account_number = randint(1000000,9999999)
        with sqlite3.connect(self.dbpath) as connection: 
            cursor = connection.cursor()
            INSERTSQL = """INSERT INTO accounts(first_name, last_name, 
                                                username, email_address, 
                                                password_hash, balance, 
                                                account_number, admin) 
                            VALUES (:first_name, :last_name, 
                                    :username, :email_address, 
                                    :password_hash, :balance, 
                                    :account_number, :admin); """
            values = {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "username": self.username,
                "email_address": self.email_address,
                "password_hash": self.password_hash, 
                "balance": self.balance, 
                "account_number": self.account_number,
                "admin": self.admin
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
            UPDATESQL = """UPDATE accounts
                            SET first_name=:first_name, last_name=:last_name, 
                                username=:username, email_address=:email_address, 
                                password_hash=:password_hash, balance=:balance, 
                                account_number=:account_number, admin=:admin
                            WHERE id=:id;"""
            values = {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "username": self.username,
                "email_address": self.email_address,
                "password_hash": self.password_hash, 
                "balance": self.balance, 
                "account_number": self.account_number,
                "admin": self.admin,
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
            DELETESQL = """DELETE FROM accounts WHERE id=:id """
            cursor.execute(DELETESQL, {"id": self.id})
            self.id = None


    @classmethod
    def from_id(cls, id):
        """ return an object of this class for the given database row id """
        SELECTSQL = "SELECT * FROM accounts WHERE id=:id;"
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
            SELECTSQL = "SELECT * FROM accounts;"
            cursor.execute(SELECTSQL)
            result = []
            for dictrow in cursor.fetchall():
                result.append(cls(**dictrow))
            return result


    @classmethod
    def delete_all(cls):
        """ delete all rows from this table """
        with sqlite3.connect(cls.dbpath) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            SQL = "DELETE FROM accounts;"
            cursor.execute(SQL)


    def __repr__(self):
        """ return a string representing this object """
        # this is a good default __repr__
        # Q: using the docs, can you figure out what this is doing?
        return f"<{type(self).__name__} {self.__dict__}>"


    def set_password_hash(self, password):
        """ hash the provided password and set self.password_hash """
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode(), salt)

    @classmethod
    def get_from_username(cls, username):
        SELECTSQL = "SELECT * FROM accounts WHERE username=:username;"
        with sqlite3.connect(cls.dbpath) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            try:
                cursor.execute(SELECTSQL, {"username": username})
            except sqlite3.IntegrityError:
                raise ValueError("ID (id) not set in datebase.")
            dictrow = cursor.fetchone()
            if dictrow:
                return cls(**dictrow)
            return None


    @classmethod
    def login(cls, username, password):
        """ check search for username and check password, return an object of this 
        class if it matches, None otherwise """
        # is checkaccount 'safer' inside the if-statement or the same by being outside?
        checkaccount = cls.get_from_username(username)
        if checkaccount:
            if bcrypt.checkpw(password.encode(), checkaccount.password_hash): 
                return checkaccount
        return None


    def get_position_for(self, ticker):
        """ return the Position object for this account's holdings in a given
        stock, return a new 0 share position if it does not exist.
        
        Why? To make buy simple, you always just get the current position and 
        add to it. """
        return position.Position.from_account_id_and_ticker(self.id, ticker)
    

    def get_positions(self):
        """ return all Position objects for this account with more than 0 shares """
        return position.Position.all_from_account_id(self.id)
    

    def get_trades_for(self, ticker):
        """ return all Trade objects for this account and a given ticker """
        return trade.Trade.all_from_account_id_and_ticker(self.id, ticker)
    

    def get_trades(self):
        """ return all Trades this account has made """
        return trade.Trade.all_from_account_id(self.id)
    

    def buy(self, ticker, volume):
        """ Create a trade and modify a position for this user, creating a buy. 
        Can raise errs.InsufficientFundsError or errs.NoSuchTickerError """
        if volume <= 0:
            raise errs.VolumeLessThanZeroError

        buy_trade = Trade(ticker=ticker, volume=volume, account_id=self.id)
        if trade.get_current_price(ticker) is None:
            raise errs.NoSuchTickerError
        else:
            buy_trade.unit_price = trade.get_current_price(ticker) 
        if self.balance < buy_trade.volume * buy_trade.unit_price:
            raise errs.InsufficientFundsError

        increase_position = Position.from_account_id_and_ticker(account_id=buy_trade.account_id, ticker=buy_trade.ticker)
        if increase_position.id:
            increase_position.shares += buy_trade.volume
        else: # sets data if position didn't exists
            increase_position.ticker = buy_trade.ticker
            increase_position.shares = buy_trade.volume
            increase_position.account_id = buy_trade.account_id
        increase_position.save()

        buy_trade.save()


    def sell(self, ticker, volume):
        """ Create a trade and modify a position for this user, creating a sell.
        Can raise errs.InsufficientSharesError or errs.NoSuchTickerError """
        if volume <= 0: 
            raise errs.VolumeLessThanZeroError

        sell_trade = Trade(ticker=ticker, volume=volume, account_id=self.id)
        if trade.get_current_price(ticker) is None:
            raise errs.NoSuchTickerError
        else:
            sell_trade.unit_price = trade.get_current_price(ticker)
        
        decrease_position = Position.from_account_id_and_ticker(account_id=sell_trade.account_id, ticker=sell_trade.ticker)
        if decrease_position.shares < sell_trade.volume:
            raise errs.InsufficientSharesError
        decrease_position.shares -= sell_trade.volume
        decrease_position.save()

        sell_trade.volume *= -1 # Differentiates buys/sells with pos/negative volume
        sell_trade.save()


    def stock_quotes(self, ticker):
        stock_quote = trade.get_current_price(ticker)
        if stock_quote:
            return stock_quote
        raise errs.NoSuchTickerError


    def is_admin(self):
        if Account.admin == 1:
            return True
        return False