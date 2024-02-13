from flask import Flask, request, json, render_template
import hmac
import hashlib
import datetime
import os
from nylas import Client
import os
from dataclasses import dataclass

webhooks = []

@dataclass
class Webhook():
    _id: str
    date: str
    title: str
    description: str
    participants: str
    status: str

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

    if request.method == "POST":
        is_genuine = verify_signature(
            message=request.data,
            key=os.environ['CLIENT_SECRET'].encode("utf8"),
            signature=request.headers.get("X-Nylas-Signature")
        )
    
        if not is_genuine:
            return "Signature verification failed!", 401
        print(is_genuine)
        query_params = {"calendar_id": os.environ['CALENDAR_ID']}
        print(query_params)
        data = request.get_json()
        print(f"Data: {data}")
        event, _ = nylas.events.find(identifier = os.environ['GRANT_ID'], event_id = data["data"]["object"]["id"], query_params = query_params)
        match event.when.object:
            case 'timespan':
                start_time = pendulum.from_timestamp(event.when.start_time, today.timezone.name).strftime("%d/%m/%Y at %H:%M:%S")
                end_time = pendulum.from_timestamp(event.when.end_time, today.timezone.name).strftime("%d/%m/%Y at %H:%M:%S")
                event_date = f"From: {start_time} to {end_time}"
            case 'datespan':
                start_time = pendulum.from_timestamp(event.when.start_date, today.timezone.name).strftime("%d/%m/%Y")
                end_time = pendulum.from_timestamp(event.when.end_date, today.timezone.name).strftime("%d/%m/%Y")
                event_date = f"From: {start_time} to {end_time}"
            case 'date':
                event_date = f"On: {event.when.date}" 
        for participant in event.participants:
            participant += f"{participant.email};"
                
        hook = Webhook(event.id, event_date, event.title, event.description, participant[:-1], event.status)
        webhooks.append(hook)
        return "Webhook received", 200

@app.route("/")
def index():
    return render_template('main.html', webhooks = webhooks)

def verify_signature(message, key, signature):
    digest = hmac.new(key, msg=message, digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature)
        
# Run our application
if __name__ == "__main__":
    app.run()       
