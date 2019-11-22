import bcrypt
import sqlite3
import unittest
from app import Account, Trade, Position, setDB
from app import InsufficientFundsError, InsufficientSharesError, NoSuchTickerError
from schema import schema
from tests.config import DBPATH


class TestAccount(unittest.TestCase):

    @classmethod 
    def setUpClass(cls):
        schema(DBPATH)
        setDB(DBPATH)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        with sqlite3.connect(DBPATH) as connection:
            cursor = connection.cursor()
            DELETESQL = "DELETE FROM accounts;"
            cursor.execute(DELETESQL)
    
    def tearDown(self):
        pass

    def test_dummy(self):
        self.assertTrue(True)
    
    def testSaveInsert(self):
        caroline = Account(username="cg16" , password_hash="password" , balance=10000, 
        first_name="Caroline", last_name="Grabowski", email="caroline.gbowksi@gmail.com")
        caroline.save()
        self.assertIsNotNone(caroline.id, "save should set an id value for new input")
        with sqlite3.connect(DBPATH) as connection:
            cursor = connection.cursor()
            SQL = "SELECT * FROM accounts WHERE username='cg16';"
            cursor.execute(SQL)
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 1, "save should create 1 new row in the database")

    def testSaveUpdate(self):
        caroline = Account(username="cg16" , password_hash="password" , balance=10000, 
        first_name="Caroline", last_name="Grabowski", email="caroline.gbowksi@gmail.com")
        caroline.save()
        caroline_id = caroline.id
        caroline2 = Account.from_id(caroline_id)
        caroline2.username = "cgrabow16"
        caroline2.balance = 20000
        caroline2.first_name = "Caro"
        caroline2.last_name = "Grabo"
        caroline2.save()
        self.assertEqual(caroline2.id, caroline_id, "update should not change ID number")

        caroline3 = Account.from_id(caroline_id)
        self.assertEqual(caroline3.username, "cgrabow16", "update should update username")
        self.assertEqual(caroline3.balance, 20000 , "update should update balance")
        self.assertEqual(caroline3.first_name, "Caro" , "update should update name")
        self.assertEqual(caroline3.last_name, "Grabo" , "update should update name")

    def testDelete(self):
        caroline = Account(username="cg16" , password_hash="password" , balance=10000, 
        first_name="Caroline", last_name="Grabowski", email="caroline.gbowksi@gmail.com")
        caroline.save()
        alex = Account(username="alex16" , password_hash="password" , balance=20000, 
        first_name="Alex", last_name="C", email="alexc@gmail.com")
        alex.save()
        caroline.delete()
        with sqlite3.connect(DBPATH) as connection: 
            cursor = connection.cursor()
            SQL = "SELECT * FROM ACCOUNTS WHERE balance=10000;"
            cursor.execute(SQL)
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 0, "delete should delete 1 row in the table")

    def testDeleteAll(self):
        caroline = Account(username="cg16" , password_hash="password" , balance=10000, 
        first_name="Caroline", last_name="Grabowski", email="caroline.gbowksi@gmail.com")
        caroline.save()
        alex = Account(username="alex16" , password_hash="password" , balance=20000, 
        first_name="Alex", last_name="C", email="alexc@gmail.com")
        alex.save()
        Account.delete_all()
        with sqlite3.connect(DBPATH) as connection: 
            cursor = connection.cursor()
            SQL = "SELECT * FROM ACCOUNTS;"
            cursor.execute(SQL)
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 0, "delete all should delete all rows in the table")

    def testFromId(self):
        caroline = Account(username="cg16", password_hash="password", balance=10000, 
        first_name="Caroline", last_name="Grabowski", email="caroline.gbowksi@gmail.com")
        caroline.save()
        caroline_id = caroline.id
        caroline2 = Account.from_id(caroline_id)
        self.assertEqual(caroline2.first_name, "Caroline")
        alex = Account.from_id(10340923950399)
        self.assertIsNone(alex, "from_id returns None for nonexistent row")

    def testAll(self):
        caroline = Account(username="cg16", password_hash="password", balance=10000, 
                           first_name="Caroline", last_name="Grabowski", email="caroline.gbowksi@gmail.com")
        caroline.save()
        alex = Account(username="alex16", password_hash="password", balance=20000, 
                       first_name="Alex", last_name="C", email="alexc@gmail.com")
        alex.save()

        all_data = Account.all()
        # self.assertEqual(len(all_data), 2, "all data should return all rows of data")
        self.assertEqual(all_data[0].first_name, "Caroline", "all function should return all account data")
        self.assertEqual(all_data[1].first_name, "Alex", "all function should return all account data")

    def testPasswordHash(self):
        # TEST that set_password_hash actually returns a hashed password
        caroline = Account(username="cg16" , balance=10000, first_name="Caroline", last_name="Grabowski", email="caroline.gbowksi@gmail.com")
        caroline.save()
        caroline.set_password_hash("password")
        self.assertIsNotNone(caroline.password_hash, "password_hash should return a hashed password")

        # TEST that set_password_hash actually hashed password correctly
        # it worked due to grit, not skill
        self.assertTrue(bcrypt.checkpw("password".encode(), caroline.password_hash), msg="set_password hash() should set self.hashed_password to encrypted password")


    def testBuy(self):
        alex = Account(username="alex16", password_hash="password", balance=20000000, 
                       first_name="Alex", last_name="C", email="alexc@gmail.com")
        alex.save()

        # Tests buy for an already existing position
        stok_position = Position(ticker="STOK", shares=100, account_id=alex.id)
        stok_position.save()
        alex.buy(ticker="STOK", volume=100)
        check_stok = Position.from_account_id_and_ticker(account_id=alex.id, ticker="STOK")
        self.assertEqual(check_stok.shares, 200, msg="buy() should increase position shares")

        # Tests buy trade for a position that doesn't exist
        alex.buy(ticker="P2P", volume=101)
        check_p2p = Position.from_account_id_and_ticker(account_id=alex.id, ticker="P2P")
        self.assertEqual(check_p2p.shares, 101, "buy() should increase position shares")


        # Test bad ticker symbol
        with self.assertRaises(NoSuchTickerError, msg="buy() should raise NoSUchTickerError"):
            alex.buy(ticker="xyz1234", volume=100)

    def testSell(self):
        caroline = Account(username="cg16", password_hash="password", balance=10000, 
                           first_name="Caroline", last_name="Grabowski", email="caroline.gbowksi@gmail.com")
        caroline.save()

        # Tests sell for a position with SUFFICIENT shares
        a33a_position = Position(ticker="A33A", shares=200, account_id=caroline.id)
        a33a_position.save()
        caroline.sell(ticker="A33A", volume=100)
        check_a33a = Position.from_account_id_and_ticker(account_id=caroline.id, ticker="A33A")
        self.assertEqual(check_a33a.shares, 100, "sell() should decrease position shares")

        # Tests sell for a position with INSUFFICIENT shares
        stok_position = Position(ticker="STOK", shares=100, account_id=caroline.id)
        stok_position.save()
        with self.assertRaises(InsufficientSharesError, msg="sell() should raise InsufficicentSharesError"):
            caroline.sell(ticker="STOK", volume=200)

        # Tests sell trade for a position that doesn't exist
        with self.assertRaises(InsufficientSharesError, msg="sell() should raise InsufficicentSharesError"):
            caroline.sell(ticker="P2P", volume=202)

        # Test bad ticker symbol
        with self.assertRaises(NoSuchTickerError, msg="sell() should raise NoSUchTickerError"):
            caroline.sell(ticker="xyz1234", volume=100)


    def testIs_admin(self):
        alex = Account(username="alex16", password_hash="password", balance=20000000, 
                       first_name="Alex", last_name="C", email="alexc@gmail.com",
                       admin=1)
        alex.save()
        self.assertEqual(alex.admin, 1, msg="account should be admin account")

        caroline = Account(username="cg16", password_hash="password", balance=10000, 
                           first_name="Caroline", last_name="Grabowski", email="caroline.gbowksi@gmail.com")
        caroline.save()
        self.assertEqual(caroline.admin, 0, msg="account should not be admin account")


########### TRACER PRINT -AKA- TOILET PAPER FUNCTION #####################################
########### WHY TOLIET PAPER? BECAUSE IT PRINTS CRAP CODE ON DISPOSOBALE "PAPER" #########
import inspect

class Tracer():

    def tp(self, var):
        callers_local_vars = inspect.currentframe().f_back.f_locals.items()
        for var_name, var_value in callers_local_vars:
            if var_value is var:
                name = var_name
        frameinfo = inspect.getframeinfo(inspect.currentframe())
        print("TRACER line", frameinfo.lineno, name + ":", var)