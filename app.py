from flask import Flask, request, json, render_template
import hmac
import hashlib
import datetime
import os
from nylas import Client
import os

# Initialize Nylas client
nylas = Client(
    api_key = os.environ['V3_API_KEY']
)

# Create the Flask app and load the configuration
app = Flask(__name__)

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
# We are connected to Nylas, let’s give back the challenge
	if request.method == "GET" and "challenge" in request.args:
		print(" * Nylas connected to the webhook!")
		return request.args["challenge"]
