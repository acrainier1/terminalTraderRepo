from flask import Flask, request, jsonify
from app import view
from app import account
from app import errs

app = Flask(__name__)

Account = account.Account


@app.route('/api', methods=["GET"])
def send_status():
    return jsonify({"status":"Running"})


@app.route('/api/price/<ticker>', methods=["GET"])
def get_price(ticker):
    acct = Account(first_name="Firstname", last_name="Lastname",
                   username="fnln1", email_address="fnln@mail.com",
                   balance=1000.00)
    acct.set_password_hash("password")
    acct.save()
    return jsonify({f"{ticker} price": acct.stock_quotes(ticker)})


@app.route('/api/<api_key>/balance', methods=["GET"])
def get_balance(api_key):
    # test api_key = 976941427
    acct = Account.from_api_key(api_key)
    return jsonify({f"{acct.username} balance": acct.balance})


@app.route('/api/<api_key>/positions', methods=["GET"])
def get_positions(api_key):
    # test api_key = 445783670
    acct = Account.from_api_key(api_key)
    print(acct.get_positions())
    list_positions = acct.get_positions()
    positions = [{"ticker": position.ticker, 
                  "shares": position.shares} for position in list_positions]
    return jsonify({f"{acct.username} positions": positions})


@app.route('/api/<api_key>/trades', methods=["GET"])
def get_trades(api_key):
    # test api_key = 445783670
    acct = Account.from_api_key(api_key)
    list_trades = acct.get_trades()
    trades = [{"ticker": trade.ticker, 
               "volume": trade.volume, 
               "time": trade.time,
               "unit_price": trade.unit_price} for trade in list_trades]
    return jsonify({f"{acct.username}'s trades": trades})


@app.route('/api/<api_key>/trades/<ticker>', methods=["GET"])
def get_trades_for(api_key, ticker):
    # test api_key = 445783670
    acct = Account.from_api_key(api_key)
    list_trades = acct.get_trades_for(ticker)
    trades = [{"ticker": trade.ticker, 
               "volume": trade.volume, 
               "time": trade.time,
               "unit_price": trade.unit_price} for trade in list_trades]
    return jsonify({f"{acct.username}'s {ticker} trades": trades})


@app.route('/api/<api_key>/deposit', methods=["PUT"])
def make_deposit(api_key):
    data = request.get_json()
    # test api_key = 445783670
    acct = Account.from_api_key(api_key)
    amount = round(float(data["amount"]), 2)
    old_balance = acct.balance
    acct.balance += amount
    acct.save()
    return jsonify({f"{acct.username}'s balance": [{"OLD": "{:.2f}".format(old_balance),
                                                    "NEW": "{:.2f}".format(acct.balance)}] })


@app.route('/api/<api_key>/sell', methods=["POST"])
def sell_order(api_key):
    data = request.get_json()
    # test api_key = 445783670
    acct = Account.from_api_key(api_key)
    ticker = data["ticker"]
    volume = data["volume"]
    acct.sell(ticker, volume)
    acct.save()
    return jsonify({f"{acct.username}'s sell order": [{"TICKER": ticker,
                                                       "VOLUME": volume}] })


@app.route('/api/<api_key>/buy', methods=["POST"])
def buy_order(api_key):
    data = request.get_json()
    # test api_key = 445783670
    acct = Account.from_api_key(api_key)
    ticker = data["ticker"]
    volume = data["volume"]
    acct.buy(ticker, volume)
    acct.save()
    return jsonify({f"{acct.username}'s buy order": [{"TICKER": ticker,
                                                      "VOLUME": volume}] })


if __name__ == '__main__':
    app.run(debug=True)


"""
curl -d '{"amount": 3.50}' -H "Content-Type: application/json" -X PUT http://localhost:5000/api/445783670/deposit

curl -d '{"ticker": "aapl", "volume": 5}' -H "Content-Type: application/json" -X POST http://localhost:5000/api/445783670/sell

curl -d '{"ticker": "tsla", "volume": 2}' -H "Content-Type: application/json" -X POST http://localhost:5000/api/445783670/buy

"""