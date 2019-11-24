import fnmatch

# The Viewer prints to the terminal based on user's actions
# and choice from the Terminal Trader menus


def welcome():
    print("\nWelcome to Terminal Trader!\n")

## IF QUIT
def goodbye():
    print("\nThank you! Good bye.\n")
 

## LOGIN MENU - OPTIONS FOR ALL USERS
def print_login_menu():
    """ displays login menu"""
    print("""
=========================

    --- LOGIN MENU ---

    [1] Create account
    [2] Log in
    [3] Quit
""")

def choice_menu_prompt():
    """ prompts user to input choice from login or main menu"""
    return input("      Your choice: ")

def bad_choice_input():
    """ if bad choice, tells user that choice not recognized"""
    print("\nInput not recognized! Please try again.\n")


##      IF LOG IN 
#       GATHERING LOGIN DATA
def login_username():
    """ if user logs in, gathers username from user"""
    return input("\nUsername: ")

def login_password():
    """ if user logs in, gathers password from user"""
    return input("Password: ")


#       IF BAD LOGIN
def bad_login_input():
    """ if bad login, tells user that login not recognized"""
    print("\nAccount info not recognized! Please try again.")
    print("\n=========================\n")


#       IF SUCCESSFUL LOGIN
def print_main_menu(account):
    """ if user successfully logs in, prints main menu options"""
    print(f"""
=========================
Hello, {account.first_name} {account.last_name} ({account.account_number})

    --- MAIN MENU ---

    [1] Check balance
    [2] Deposit funds
    [3] Buy and sell stocks
    [4] Look up stock quotes
    [5] View positions
    [6] Review trade history
    [7] Sign out
""")


def print_admin_menu(account):
    """ if user successfully logs in, prints main menu options"""
    print(f"""
=========================
Hello, {account.first_name} {account.last_name} ({account.account_number})

    --- MAIN MENU ---

    [1] Check balance
    [2] Deposit funds
    [3] Buy and sell stocks
    [4] Look up stock quotes
    [5] View positions
    [6] Review trade history
    [7] Sign out
    [8] Account holdings
    [9] Grant admin access
""")


#### MAIN MENU OPTIONS
# if user chooses withdraw

def give_balance(balance):
    print("\nYour balance is: ${:.2f}\n".format(balance))

def enter_deposit_info():
    return input("\nHow much to deposit? $")

def ticker_info():
    return input("\nEnter ticker symbol: ")

def bad_ticker():
    return input("\nTicker symbol not found!\nPrease ENTER to continue.")

def buy_sell_choice():
    return input("\nEnter 1 to BUY or enter 2 to SELL. ")

def enter_buy_info():
    return input("\nHow much to buy? $")

def enter_sell_info():
    return input("\nHow much to sell? $")

def bad_number_input():
    print("\nEnter number greater than 0! Please try again.")

def stock_info(ticker, stock_quote):
    print("\nThe current price for " + str(ticker).upper() + " is $" + str(stock_quote).upper())

def insufficient_funds():
    print("\nInusfficient funds!")

def insufficient_shares():
    print("\nInusfficient shares!")

def positions_info(positions):
    print("\nBelow is a list of all your positions:\nTICKER  SHARES\n")
    for item in positions:
        print(item.ticker, " ", item.shares,"\n")

def trades_info(trades):
    print("Below is your trade history:\n")
    print("TICKER  VOLUME  PRICE   TIME\n")
    for item in trades:
        print(item.ticker, " ", item.volume, " ", item.unit_price, " ", item.time,"\n")

def all_account_positions(list_values):
    print("Below is all account position data:\n")
    print("Account ID  Total        Ticker  Shares   Price")
    for value in list_values:
        print(f"{value[0]}           ${value[1]}     {value[2]}   {value[3]}   ${value[4]}")

def grant_admin():
    return input("Enter username to grant admin access to: ")        


## IF CHOOSE CREATE ACCOUNT 
#       GATHERING ACCOUNT DATA
def new_account_creation():
    """ prints instructions for new account creation"""
    print("""\nAccount Creation\n
Enter the following information to create your account.\n""")

def first_name():
    """ gets first name from new customer"""
    return input("First Name: ")

def first_name_warning():
    print("Please enter letters only.\n")

def last_name():
    """ gets last name from new customer"""
    return input("Last Name: ")

def last_name_warning():
    print("Please enter letters only.\n")

def username():
    """ gets username from new customer"""
    return input("Create a username: ")

def username_warning():
    print("Please enter at least five characters.\n")

def email_address():
    """ gets email address from new customer"""
    return input("Email address: ")

def email_address_warning():
    print("""Please enter an email with this format:\n
name@domain.extension Example:\n`johnsmith@smail.com`\n""")

def balance():
    """ gets initial balance from new customer"""
    return input("Initial deposit to balance: $")

def balance_warning():
    print("Please enter an amount greater than $0.00.\n")

def password():
    """ gets new password from new customer"""
    return input("Set a password: ")

def password_warning():
    print("Please enter at least five characters.")

def confirm_password():
    """ confirms password from new customer"""
    return input("Confirm password: ")

def password_not_confirmed():
    print("\nPasswords do not match! Please try again.\n")

def account_number(new_account_number):
    return print("\nAccount Created\nYour new account number is: " 
            + str(new_account_number) + "\n========================\n")


