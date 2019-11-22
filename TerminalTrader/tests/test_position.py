import unittest
import sqlite3 
from app import Account, Trade, Position, setDB
from app import InsufficientFundsError, InsufficientSharesError, NoSuchTickerError
from schema import schema
from tests.config import DBPATH


class TestPosition(unittest.TestCase):

    @classmethod 
    def setUpClass(cls):
        schema(DBPATH)
        setDB(DBPATH)
    
    @classmethod
    def tearDownClass(cls):
        # called once when all the tests in this file are done
        # os.remove(DBPATH)
        pass

    def setUp(self):
        with sqlite3.connect(DBPATH) as connection:
            cursor = connection.cursor()
            DELETESQL = "DELETE FROM positions;"
            cursor.execute(DELETESQL)
            # apple = Position(ticker="AAPL", shares=100, account_id=3)
            # apple.save()
            # self.apple_id = apple.id
    
    def tearDown(self):
        pass

    def test_dummy(self):
        self.assertTrue(True)
    
    def testSaveInsert(self):
        apple = Position(ticker="AAPL", shares=100, account_id=3)
        apple.save()
        self.assertIsNotNone(apple.id, "save should set an id value for new input")
        with sqlite3.connect(DBPATH) as connection:
            cursor = connection.cursor()
            SQL = "SELECT * FROM positions WHERE shares=100;"
            cursor.execute(SQL)
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 1, "save should create 1 new row in the database")
        
    def testSaveUpdate(self):
        apple = Position(ticker="AAPL", shares=100, account_id=3)
        apple.save()
        apple_id = apple.id
        apple2 = Position.from_id(apple_id)
        apple2.shares = 150
        apple2.save()
        self.assertEqual(apple2.id, apple_id, "update should not change ID number")

        apple3 = Position.from_id(apple_id)
        self.assertEqual(apple3.ticker,  "AAPL", "save update should keep same ticker if not changed")
        self.assertEqual(apple3.shares,  150, "save updates should increase share amt by 50")
        self.assertEqual(apple3.account_id,  3, "save should keep the same account_id if not changed")

    def testDelete(self):
        apple = Position(ticker="AAPL", shares=100, account_id=3)
        apple.save()
        orange = Position(ticker="ORNG", shares=150, account_id=3)
        orange.save()
        apple.delete()
        with sqlite3.connect(DBPATH) as connection:
            cursor = connection.cursor()
            SQL = "SELECT * FROM positions;"
            cursor.execute(SQL)
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 1, "delete should delete 1 row in the database")
    
    def testDeleteAll(self):
        apple = Position(ticker="AAPL", shares=100, account_id=3)
        apple.save()
        orange = Position(ticker="ORNG", shares=150, account_id=3)
        orange.save()
        Position.delete_all()
        with sqlite3.connect(DBPATH) as connection:
            cursor = connection.cursor()
            SQL = "SELECT * FROM positions;"
            cursor.execute(SQL)
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 0, "delete_all should delete all rows in the database")
    
    def testFromId(self):
        apple = Position(ticker="AAPL", shares=100, account_id=3)
        apple.save()
        apple_id = apple.id
        apple2 = Position.from_id(apple_id)
        self.assertEqual(apple2.ticker, "AAPL", "Data should be loaded from database with .from_id()")
        orange = Position.from_id(100000000000)
        self.assertIsNone(orange, ".from_id() returns None for nonexistent row")

    def testAll(self):
        apple = Position(ticker="AAPL", shares=100, account_id=3)
        orange = Position(ticker="ORNG", shares=150, account_id=3)
        banana = Position(ticker="BANA", shares=100, account_id=3)
        apple.save()
        orange.save()
        banana.save()

        all_data = Position.all()
        self.assertEqual(len(all_data), 3, "all data should return 3 rows of data")

        self.assertEqual(all_data[0].ticker, "AAPL", "all function should return all position data")
        self.assertEqual(all_data[1].ticker, "ORNG", "all function should return all position data")
        # self.assertEqual(apple.shares,  100, "save updates should increase share amt by 50")
        # self.assertEqual(apple.account_id,  3, "save should keep the same account_id if not changed")

        # self.assertEqual(all_data, result, "....")
        pass


    def testAllFromAccountId(self):
        apple = Position(ticker="AAPL", shares=0, account_id=3)
        orange = Position(ticker="ORNG", shares=100, account_id=3)
        banana = Position(ticker="BANA", shares=100, account_id=3)
        apple.save()
        orange.save()
        banana.save()
        account_id = apple.id
        all_account_data = Position.all_from_account_id(account_id)
        results = []
        print(all_account_data)
        self.assertEqual(all_account_data, results, "function should spit out all positions for account id where shares >0")
        pass
