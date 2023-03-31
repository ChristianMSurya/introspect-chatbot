from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import random
import schedule
import time
import threading
import os
import json
import threading


load_dotenv()

app = Flask(__name__)
app.config["DEBUG"] = True

# Example dilemmas and historical outcomes
dilemmas = [
    {
        "dilemma": "Dilemma 1: Description",
        "outcome": "Outcome 1: Historical resolution"
    },
    {
        "dilemma": "Dilemma 2: Description",
        "outcome": "Outcome 2: Historical resolution"
    },
    # Add more dilemmas here
]

# Store user phone numbers and their last received dilemma
user_data = {}

# Create a lock for synchronizing access to the user_data dictionary
user_data_lock = threading.Lock()

def send_dilemma(phone_number):
    from twilio.rest import Client

    # Your Twilio credentials
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone_number = "+18447551091"

    client = Client(account_sid, auth_token)

    # Select a random dilemma
    dilemma = random.choice(dilemmas)

    # Save the user's current dilemma
    user_data[phone_number] = {
        "dilemma": dilemma,
        "waiting_for_guess": True,
        "responses": []
    }

    # Send the dilemma to the user
    client.messages.create(
        body=dilemma["dilemma"],
        from_=twilio_phone_number,
        to=phone_number
    )

def daily_dilemmas():
    for phone_number in user_data:
        send_dilemma(phone_number)

# Schedule daily dilemmas
schedule.every().day.at("12:00").do(daily_dilemmas)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_schedule)
scheduler_thread.start()

@app.route("/sms", methods=["POST"])
def sms_reply():
    phone_number = request.form["From"]
    message_body = request.form["Body"]

    if phone_number not in user_data:
        # Add the user and send them a dilemma
        send_dilemma(phone_number)
    else:
        if user_data[phone_number]["waiting_for_guess"]:
            # The user has sent their guess, now send the historical outcome
            dilemma = user_data[phone_number]["dilemma"]
            response = {"dilemma": dilemma["dilemma"], "response": message_body}
            user_data[phone_number]["waiting_for_guess"] = False
            resp = MessagingResponse()
            resp.message(dilemma["outcome"])
            # Save the responses to a JSON file
            with open('responses.json', 'a') as f:
                json.dump(response, f)
            # Lock the user_data dictionary before modifying it
            with user_data_lock:
                user_data[phone_number]["responses"].append(response)
        else:
            # The user has received the outcome, now send a new dilemma
            send_dilemma(phone_number)
            user_data[phone_number]["waiting_for_guess"] = True
            resp = MessagingResponse()

        return str(resp)


if __name__ == "__main__":
    app.run(debug=True, port=5009)
