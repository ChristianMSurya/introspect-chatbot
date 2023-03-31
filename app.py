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
import csv

app = Flask(__name__)
app.config["DEBUG"] = True

DAILY_DILEMMAS_TIME = os.getenv('DAILY_DILEMMAS_TIME', '08:00')
load_dotenv()

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

# Map dilemma descriptions to their outcomes
dilemma_outcomes = {dilemma['dilemma']: dilemma['outcome'] for dilemma in dilemmas}




# Read the phone numbers from the responses.csv file
with open('responses.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader) # skip header row
    phone_numbers_responses = set([row[0] for row in reader])



def send_intro(phone_number):
    from twilio.rest import Client

    # Your Twilio credentials
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone_number = "+18447551091"

    client = Client(account_sid, auth_token)

    # Send the intro message to the user
    client.messages.create(
        body="Thanks for signing up to the first MVP of the Introspect Chatbot. At 8 AM PST every day, Introspect will send you a philosophical dilemma. You'll be asked to reply with what you would do. After you reply, Introspect will send you more information about what ended up happening. We will store your answer so that you can come back to them in the future. We hope that this exercise will help you introspect about your values and encourage you to do good.",
        from_=twilio_phone_number,
        to=phone_number
    )

    # Select the first dilemma in the list
    dilemma = dilemmas[0]

    # Save the user's current dilemma
    with open('responses.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([phone_number, dilemma["dilemma"], ""])

    # Send the first dilemma to the user
    send_dilemma(phone_number)

def send_dilemma(phone_number):
    from twilio.rest import Client

    # Your Twilio credentials
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone_number = "+18447551091"

    client = Client(account_sid, auth_token)

    # Check if this is a new user
    current_dilemma_index = 0
    with open('responses.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == phone_number:
                current_dilemma_index += 1

    # Select the next dilemma in the list
    dilemma = dilemmas[current_dilemma_index]

    # Save the user's current dilemma
    with open('responses.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([phone_number, dilemma["dilemma"], ""])

    # Send the dilemma to the user
    client.messages.create(
        body=dilemma["dilemma"],
        from_=twilio_phone_number,
        to=phone_number
    )

def daily_dilemmas():
    # Read the phone numbers from the phone_numbers.csv file
    with open('phone_numbers.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader) # skip header row
        phone_numbers = set([row[0] for row in reader])

    # Read the phone numbers from the current_users.csv file
    with open('current_users.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader) # skip header row
        current_users = set([row[0] for row in reader])

    # Find the phone numbers that are in the phone_numbers.csv file but not in the current_users.csv file
    phone_numbers_to_add = phone_numbers.difference(current_users)

    # Add new phone numbers to the current_users.csv file
    with open('current_users.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        for phone_number in phone_numbers_to_add:
            writer.writerow([phone_number])


# Schedule daily dilemmas
schedule.every().day.at(DAILY_DILEMMAS_TIME).do(daily_dilemmas)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

        # Read the phone numbers from the phone_numbers.csv file
        with open('phone_numbers.csv', 'r') as f:
            reader = csv.reader(f)
            phone_numbers_csv = set([row[0] for row in reader])

        # Read the phone numbers from the current_users.csv file
        with open('current_users.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader) # skip header row
            current_users = set([row[0] for row in reader])

        # Find the phone numbers that are in the phone_numbers.csv file but not in the current_users.csv file
        phone_numbers_to_add = phone_numbers_csv.difference(current_users)

        # Send the intro message to new phone numbers
        for phone_number in phone_numbers_to_add:
            # Check if the phone number already exists in current_users.csv
            with open('current_users.csv', 'r') as f:
                reader = csv.reader(f)
                if phone_number not in [row[0] for row in reader]:
                    # Phone number is new, send the intro message
                    send_intro(phone_number)

                    # Add the phone number to the current_users.csv file
                    with open('current_users.csv', 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([phone_number])

        # Call daily_dilemmas to update current_users.csv
        daily_dilemmas()



def send_daily_dilemma(phone_number):
    from twilio.rest import Client

    # Your Twilio credentials
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone_number = "+18447551091"

    client = Client(account_sid, auth_token)

    # Select a random dilemma from the list
    dilemma = random.choice(dilemmas)

    # Save the user's current dilemma
    with open('responses.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([phone_number, dilemma["dilemma"], ""])

    # Send the dilemma to the user
    client.messages.create(
        body=dilemma["dilemma"],
        from_=twilio_phone_number,
        to=phone_number
    )



# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_schedule)
scheduler_thread.start()

# Load the phone numbers from the responses.csv file into memory
with open('responses.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader) # skip header row
    phone_numbers_responses = set([row[0] for row in reader])

@app.route("/sms", methods=["POST"])
@app.route("/sms", methods=["POST"])
def sms_reply():
    phone_number = request.form["From"]
    message_body = request.form["Body"]

    # Get the user's current dilemma
    with open('responses.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == phone_number:
                current_dilemma = row[1]
                current_response = row[2]

    # Get the outcome for the user's current dilemma
    dilemma_outcome = dilemma_outcomes.get(current_dilemma)

    if current_dilemma and not current_response:
        # The user has received a new dilemma, now send it to them
        resp = MessagingResponse()
        resp.message(current_dilemma)
    elif current_dilemma and current_response:
        # The user has sent their response, now send the outcome
        resp = MessagingResponse()
        resp.message(dilemma_outcome)
        # Update the user's response in the responses.csv file
        with open('responses.csv', 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
        with open('responses.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
            for row in rows:
                if row[0] == phone_number and row[1] == current_dilemma:
                    row[2] = current_response
            writer.writerows(rows)
    else:
        # The user has not received a dilemma yet, send the intro message
        resp = MessagingResponse()
        resp.message("Thanks for signing up to the first MVP of the Introspect Chatbot. At 8 AM PT every day, Introspect will send you a philosophical dilemma. You'll be asked to reply with what you would do. After you reply, Introspect will send you more information about what ended up happening. We hope that this exercise will help you introspect about your values and encourage you to do good.")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True, port=5009)
