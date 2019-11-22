import bcrypt
import sqlite3
import unittest
from app import controller, Account, Trade, Position, setDB, view
from app import InsufficientFundsError, InsufficientSharesError, NoSuchTickerError
from schema import schema
from tests.config import DBPATH


class TestController(unittest.TestCase):

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


    # def testRun(self):
    #     controller.run()


    def testCreate_account_and_nonadmin_login(self):
        print("""\n=========================
UNIT TEST
testCreate_account_and_nonadmin_login()
<<Press 7 and 3 to quit>> and proceed to next test\n""")

        account_data = Account(username="js2020", balance=20000000, 
                                 first_name="John", last_name="Smith", 
                                 email_address="john.smith@gmail.com",
                                 admin=0)
        account_data.set_password_hash("password")
        account_data.save()

        js2020 = Account.get_from_username("js2020")
        account_data = Account.login(js2020.username, "password")
        print("TRCR test_controller.py account_data\n", account_data)
        self.assertIsNotNone(account_data, msg="login() should return account data")
        controller.main_menu(account_data)

    
    def testCreate_account_and_admin_login(self):
        print("""\n=========================
UNIT TEST
testCreate_account_and_admin_login()
!!!Wait for menu to load first!!!...
<<Press 8: ACCOUNT POSITIONS>> and then
<<Press 9: GRANT ADMIN ACCESS to username "ms2020">> and then
<<Press 7 and 3 to quit>> and proceed to next test
!!!Wait for menu to load first!!!...\n""")

        account_data = Account(username="js2020", balance=20000000, 
                                 first_name="John", last_name="Smith", 
                                 email_address="john.smith@gmail.com",
                                 admin=1)
        account_data.set_password_hash("password")
        account_data.save()

        account_data2 = Account(username="ms2020", balance=20000000, 
                                 first_name="Mary", last_name="Sue", 
                                 email_address="mary.sue@gmail.com",
                                 admin=0)
        account_data2.set_password_hash("password")
        account_data2.save()

        account_data.buy("STOK", 100)
        account_data.buy("A33A", 300)
        account_data.sell("STOK", 50)
        account_data.buy("AAPL", 999)

        account_data2.buy("AAPL", 100)
        account_data2.sell("AAPL", 100)
        account_data2.buy("GS", 200)
        account_data2.sell("GS", 100)
        account_data2.buy("MS", 200)
        account_data2.sell("MS", 100)

        js2020 = Account.get_from_username("js2020")
        account_data = Account.login(js2020.username, "password")
        self.assertIsNotNone(account_data, msg="login() should return account data")
        controller.main_menu(account_data)


        ms2020 = Account.get_from_username("ms2020")
        account_data2 = Account.login(ms2020.username, "password")
        self.assertEqual(account_data2.admin, 1, msg="control should make this account an admin")


    def testCheck_balance(self):
        print("""\n=========================
UNIT TEST
testCheck_balance()\n""")

        account_data = Account(username="js2020", balance=20000000, 
                            first_name="John", last_name="Smith", email_address="john.smith@gmail.com")
        account_data.set_password_hash("password")
        account_data.save()
        view.give_balance(account_data.balance)


    def testDeposit_funds(self):
        print("""\n=========================
UNIT TEST
testDeposit_funds()\n""")

        account_data = Account(username="js2020", balance=20000000, 
                               first_name="John", last_name="Smith", 
                               email_address="john.smith@gmail.com")
        account_data.set_password_hash("password")
        account_data.save()
        view.give_balance(account_data.balance)
        amount = round(float(view.enter_deposit_info()), 2)
        account_data.balance += amount
        account_data.save()
        view.give_balance(account_data.balance)


    def testBuy_and_sell(self):
        print("""\n=========================
UNIT TEST
testBuy_and_sell()
This test will ALWAYS say Insufficient Funds or Shares for Buy and Sell, respectively
by design. Testing graceceful error/exception handling \n""")

        account_data = Account(username="js2020", balance=20000000, 
                            first_name="John", last_name="Smith", 
                            email_address="john.smith@gmail.com")
        account_data.set_password_hash("password")
        account_data.save()

        ticker = view.ticker_info()
        trade = view.buy_sell_choice()
        if trade not in ("1", "2"):  
            view.bad_choice_input()
            return

        elif trade == "1":
            volume = float(view.enter_buy_info())
            with self.assertRaises(InsufficientFundsError, msg="should raise InsufficientFundsError"):
                view.insufficient_funds()
                account_data.buy(ticker, 1000000) 

        elif trade == "2":
            volume = float(view.enter_sell_info())
            with self.assertRaises(InsufficientSharesError, msg="should raise InsufficientSharesError"):
                view.insufficient_shares()
                account_data.sell(ticker, 1000000)


    def testLookup_stock_prices(self):
        print("""\n=========================
UNIT TEST
testLookup_stock_prices()\n""")

        account_data = Account(username="js2020", balance=20000000, 
                               first_name="John", last_name="Smith", 
                               email_address="john.smith@gmail.com")
        account_data.set_password_hash("password")
        account_data.save()

        ticker = view.ticker_info()
        try:
            stock_quote = account_data.stock_quotes(ticker)
            view.stock_info(ticker, stock_quote)
        except NoSuchTickerError:
            view.bad_ticker()


    def testView_positions(self):
        print("""\n=========================
UNIT TEST
testView_positions()\n""")

        account_data = Account(username="js2020", balance=20000000, 
                            first_name="John", last_name="Smith", 
                            email_address="john.smith@gmail.com")
        account_data.set_password_hash("password")
        account_data.save()

        account_data.buy("STOK", 100)
        account_data.buy("P2P", 200)
        account_data.buy("A33A", 300)

        positions = account_data.get_positions()
        view.positions_info(positions)
    

    def testReview_trade_history(self):
        print("""\n=========================
UNIT TEST
testReview_trade_history()\n""")

        account_data = Account(username="js2020", balance=20000000, 
                            first_name="John", last_name="Smith", 
                            email_address="john.smith@gmail.com")
        account_data.set_password_hash("password")
        account_data.save()

        account_data.buy("STOK", 100)
        account_data.buy("P2P", 200)
        account_data.buy("A33A", 300)
        account_data.sell("P2P", 100)
        account_data.sell("STOK", 50)

        trades = account_data.get_trades()
        view.trades_info(trades)
