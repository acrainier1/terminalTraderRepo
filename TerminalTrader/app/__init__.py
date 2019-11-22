from . import controller
from .errs import InsufficientFundsError, InsufficientSharesError, NoSuchTickerError
from .trade import Trade 
from .position import Position
from .account import Account

# Any name defined inside of app.__init__.py, either by importing from
# another file, defining a variable, or defining a function, will be available
# as an import directly from app. So code outside of app can use the Position
# class with 'from app import Position' or the controller's run function with
# 'from app import run'

run = controller.run


def setDB(dbpath):
    # Update the dbpath of all of the classes
    Trade.setDB(dbpath)
    Position.setDB(dbpath)
    Account.setDB(dbpath)