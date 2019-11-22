from flask import Flask, request, jsonify
from . import view
from . import account
from . import errs

app = Flask(__name__)


@app.route('/', methods=["GET"])
def send_status():
    return jsonify({"status":"Running"})