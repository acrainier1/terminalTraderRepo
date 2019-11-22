import fnmatch
from flask import Flask, request, jsonify
from . import view
from . import account
from . import errs


# a way to get around having to use the module name when avoiding
# circular import problems
Account = account.Account
# note: if you do not create any new Trade or Position objects but only
# get them as the return values from Account's methods, you do not need
# to import those classes directly. You only need to import the class
# if you need to call the constructor (t=Trade()) or call a class method

def run():
    view.welcome()
    
    while True:
        account_data = login_menu()
        if account_data is None:
            break
        main_menu(account_data)
    
    view.goodbye()


def login_menu():
    """ login, create account, or quit. return an Account object on successful login
    return None for quit """

    while True:
        view.print_login_menu()
        choice = view.choice_menu_prompt().strip()

        # Checks for valid choice in 1, 2, or 3
        if choice not in ("1", "2", "3"): 
            view.bad_choice_input()

        # [3] Quit
        elif choice == "3": 
            return None # return None to quit

        # [1] Create account
        elif choice == "1":
            create_account()

        # [2] Log in
        elif choice == "2":
            username = view.login_username().strip()
            password = view.login_password().strip()
            account_data = Account.login(username, password)
            if account_data != None:
                return main_menu(account_data)
            view.bad_login_input()


def main_menu(account_data):
    from . import InsufficientFundsError, InsufficientSharesError, NoSuchTickerError
    """ check balance, deposit, withdraw, see positions, see trades, look up stock
    prices, buy, and sell. No return value. """
    

    while True:
        if account_data.admin == 1:
            view.print_admin_menu(account_data)
        else:
            view.print_main_menu(account_data)
        choice = view.choice_menu_prompt()

        # checks for propper login choice
        if account_data.admin == 1 and choice not in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):  
            view.bad_choice_input()
            return main_menu(account_data)

        # Sign out
        elif choice == "7":      
            # Account.save()
            return login_menu()
            
        # Check balance
        elif choice == "1":
            balance = round(account_data.balance, 2)
            view.give_balance(balance)

        # Deposit funds
        elif choice == "2":
            view.give_balance(account_data.balance)
            amount = round(float(view.enter_deposit_info()), 2)
            account_data.balance += amount
            account_data.save()
            view.give_balance(account_data.balance)
            return main_menu(account_data)
            
        # Buy and sell stock
        elif choice == "3":
            ticker = view.ticker_info()
            trade = view.buy_sell_choice()
            if trade not in ("1", "2"):  
                view.bad_choice_input()
                return main_menu(account_data)
            elif trade == "1":
                volume = float(view.enter_buy_info())
                try:
                    account_data.buy(ticker, volume)
                except errs.NoSuchTickerError:
                    view.bad_ticker()
                    return main_menu(account_data)
                except InsufficientFundsError:
                    view.insufficient_funds()
                    return main_menu(account_data)

            elif trade == "2":
                volume = float(view.enter_sell_info())
                try:
                    account_data.sell(ticker, volume)
                except NoSuchTickerError:
                    view.bad_ticker()
                    return main_menu(account_data)
                except InsufficientSharesError:
                    view.insufficient_shares()
                    return main_menu(account_data)
            return main_menu(account_data)


        # Look-up stock quotes
        elif choice == "4":
            ticker = view.ticker_info()
            try:
                stock_quote = account_data.stock_quotes(ticker)
                view.stock_info(ticker, stock_quote)
            except NoSuchTickerError:
                view.bad_ticker()
                return main_menu(account_data)

        # View positions
        elif choice == "5":
            positions = account_data.get_positions()
            view.positions_info(positions)
            return main_menu(account_data)
    
        # Review trade history
        elif choice == "6":
            trades = account_data.get_trades()
            view.trades_info(trades)
            return main_menu(account_data)

        # view all account data
        elif choice == "8":
            if account_data.admin == 1:
                data_for_admin(account_data)
            else:
                view.bad_choice_input()
            return main_menu(account_data)

        # Grant admin access to other account holders
        elif choice == "9":
            if account_data.admin == 1:
                username = view.grant_admin()
                other_account = account_data.get_from_username(username)
                other_account.admin = 1
                other_account.save()
            else:
                view.bad_choice_input()
            return main_menu(account_data)


def create_account(): 
    """ called from main menu if account_data chooses create account"""
    """ call this from the main login loop """
    view.new_account_creation()

    while True: # Gets first name
        first_name = view.first_name()
        if first_name.isalpha() and len(first_name) > 0:
            break
        view.first_name_warning()

    while True: # Gets last name
        last_name = view.last_name()
        if last_name.isalpha() and len(last_name) > 0:
            break
        view.last_name_warning()

    while True: # Gets username
        username = view.username()
        if len(username) > 4:
            break
        view.username_warning()

    while True: # Gets email address
        email_address = [view.email_address()]
        email = fnmatch.filter(email_address, '*@*.*')
        if email != []:
            if email_address[0][0] != "@" and email_address[0][len(email_address[0])-1] != ".":
                email_address = email_address[0]
                break
        view.email_address_warning()

    while True: # Gets initial balance
        balance = float(view.balance())
        if balance > 0 :
            break
        view.balance_warning()

    while True: # Gets password
        password = view.password()
        if len(password) > 4:
            break
        view.password_warning()

    while True: # Confirms password
        confirm_password = view.confirm_password()
        if password == confirm_password:
            new_client = Account(first_name=first_name, last_name=last_name,
                                username=username, email_address=email_address,
                                balance=balance)
            new_client.set_password_hash(password)
            new_client.save()
            new_account_number = new_client.account_number
            view.account_number(new_account_number)    
            break
        view.password_not_confirmed()


def data_for_admin(account_data):
    all_data = account_data.all()

    # first gets LISTS of position objs then....
    list_positions = []
    for row in all_data:
        acct = Account.from_id(row.id)
        raw_list = acct.get_positions()
        for position in raw_list: #...then it extracts individuals positions
            list_positions.append(position)

    list_values = []
    for position in list_positions:
        value = position.shares * account_data.stock_quotes(position.ticker)
        list_values.append([position.account_id, value,
                            position.ticker, position.shares, 
                            account_data.stock_quotes(position.ticker)] )
    def onFourth(elem):
        return elem[3]
    list_values.sort(key=onFourth, reverse=True)
    view.all_account_positions(list_values)
     

if __name__ == "__main__":
    # app.run(debug=True)
    run()