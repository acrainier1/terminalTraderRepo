import unittest
import sqlite3
from app import Account, Trade, Position, setDB
from app import InsufficientFundsError, InsufficientSharesError, NoSuchTickerError
from schema import schema
from tests.config import DBPATH


class TestTrade(unittest.TestCase):
    

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
        # called once before EACH test method
        with sqlite3.connect(DBPATH) as connection:
            cursor = connection.cursor()
            DELETESQL = "DELETE FROM trades;"
            cursor.execute(DELETESQL)



    def tearDown(self):
        # called once after EACH test method
        pass

    
    ##### TESTS FOR REGULAR CLASS METHODS #####

    def test_dummy(self):
        self.assertTrue(True)


    def testSaveInsert(self):
        # First trade instance to initialize data on row 1
        trade = Trade(ticker="IBM", volume=100.0, unit_price=11.22, account_id="1234567")
        trade.save()
        self.assertIsNotNone(trade.id, "save should set an ID value")
        with sqlite3.connect(Trade.dbpath) as connection:
            cursor = connection.cursor()
            SQL = "SELECT * FROM trades WHERE ticker='IBM' AND account_id='1234567';"
            cursor.execute(SQL)
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 1, "save should create a row in the database")


    def testSaveUpdate(self):
        # First trade instance to initialize data on row 2
        trade = Trade(ticker="GS", volume=100.0, unit_price=33.44, account_id="7654321")
        trade.save()
        self.assertIsNotNone(trade.id, "save() should set an ID value")
        self.assertEqual(trade.unit_price, 33.44, "unit_price was saved")

        # Second trade instance with same id to update data
        trade2 = Trade.from_id(trade.id)
        self.assertEqual(trade2.unit_price, 33.44, "unit_price was saved")
        trade2.ticker = "AAPL"
        trade2.volume = 200.0
        trade2.unit_price = 55.66
        trade2.account_id = "7654321"
        trade2.save()
        self.assertEqual(trade2.id, trade.id, "save() doesn't create new row for existing account")
        
        # Third instance which should be all updated to compare second one with
        trade3 = Trade.from_id(trade.id)
        self.assertEqual(trade3.ticker, "AAPL", "ticker should be updated")
        self.assertEqual(trade3.unit_price, 55.66, "unit_price should be updated")
        self.assertEqual(trade3.volume, 200.00, "volume should be updated")
        self.assertNotEqual(trade3.time, trade.time, "time should be updated")


    def testDelete(self):
        # First trade instance to initialize data
        trade = Trade(ticker="GS", volume=1100.0, unit_price=77.88, account_id="7654321")
        trade.delete()

        with sqlite3.connect(Trade.dbpath) as connection:
            cursor = connection.cursor()
            SELECTSQL = "SELECT * FROM trades WHERE id='1';"
            cursor.execute(SELECTSQL)
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 0, "delete() should delete DB rows")


    ##### TESTS FOR @classmethod FUNCTIONS #####

    def testFromId(self):
        # First trade instance to initialize data
        trade = Trade(ticker="GS", volume=1234.0, unit_price=77.88, account_id="7654321")
        trade.save()
        trade2 = Trade.from_id(trade.id)
        self.assertEqual(trade.id, trade2.id, "fromId() should return identical object from instance")

    
    def testAll(self):
        # Three trade instances to initialize data
        trade0 = Trade(ticker="IBM", volume=100.0, unit_price=11.22, account_id="1111111")
        trade0.save()
        trade1 = Trade(ticker="GS", volume=200.0, unit_price=33.44, account_id="2222222")
        trade1.save()
        trade2 = Trade(ticker="AAPL", volume=300.0, unit_price=55.66, account_id="3333333")
        trade2.save()

        all_data = Trade.all()
        self.assertEqual(len(all_data), 3, "all() should return all rows from Trades table")
        self.assertEqual(all_data[0].ticker, "IBM", "all() should return correct ticker data")
        

    def testDelete_all(self):
        # Three trade instances to initialize data
        trade0 = Trade(ticker="IBM", volume=100.0, unit_price=11.22, account_id="1111111")
        trade0.save()
        trade1 = Trade(ticker="GS", volume=200.0, unit_price=33.44, account_id="2222222")
        trade1.save()
        trade2 = Trade(ticker="AAPL", volume=300.0, unit_price=55.66, account_id="3333333")
        trade2.save()

        Trade.delete_all()
        with sqlite3.connect(DBPATH) as connection:
            cursor = connection.cursor()
            SQL = "SELECT * FROM positions;"
            cursor.execute(SQL)
            rows = cursor.fetchall()
            self.assertEqual(len(rows), 0, "delete_all should delete all rows in the database")
    
    def testAll_from_account_id(self):
        # Three trade instances to initialize data
        trade0 = Trade(ticker="IBM", volume=100.0, unit_price=11.22, account_id="1111111")
        trade0.save()
        trade1 = Trade(ticker="GS", volume=200.0, unit_price=33.44, account_id="2222222")
        trade1.save()
        trade2 = Trade(ticker="AAPL", volume=300.0, unit_price=55.66, account_id="1111111")
        trade2.save()

        all_data = Trade.all_from_account_id(trade0.account_id)
        self.assertEqual(all_data[0].account_id, all_data[1].account_id, "all_from_account_id() should only return same account_id data")


    def testAll_from_account_id_and_ticker(self):
        # Three trade instances to initialize data
        trade0 = Trade(ticker="IBM", volume=100.0, unit_price=11.22, account_id="1111111")
        trade0.save()
        trade1 = Trade(ticker="IBM", volume=200.0, unit_price=33.44, account_id="1111111")
        trade1.save()
        trade2 = Trade(ticker="AAPL", volume=300.0, unit_price=55.66, account_id="1111111")
        trade2.save()

        all_data = Trade.all_from_account_id_and_ticker(trade0.account_id, trade0.ticker)
        self.assertEqual(len(all_data), 2, "all_from_account_id_and_ticker() should only return rows WHERE 2 conditions are met")
        self.assertEqual(all_data[0].account_id, all_data[1].account_id, "all_from_account_id_and_ticker() should only return same account_id data")
        self.assertEqual(all_data[0].ticker, all_data[1].ticker, "all_from_account_id_and_ticker() should only return same ticker data")


    def testGet_account(self):
        trade = Trade(account_id="9999999")
        accountTest = trade.get_account()


    def testGet_position(self):
        trade = Trade(account_id="9999999")
        positionTest = trade.get_position()
