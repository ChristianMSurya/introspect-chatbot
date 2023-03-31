import os
import csv
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import schedule
import time
import threading
from dotenv import load_dotenv

app = Flask(__name__)
app.config["DEBUG"] = True

DAILY_DILEMMAS_TIME = os.getenv('DAILY_DILEMMAS_TIME', '10:00')
load_dotenv()

# Replace these with your desired dilemma and outcome
dilemma = "Introspect 1: Imagine that you and your friends created a very popular product that revolutionized its market, generating over $1B per year. However, it was later discovered that it had unintended negative health consequences. What would you do? Would you keep selling or halt production? How would you communicate with the public?"
outcome = "Today's dilemma is based on the company called Juul. In 2015, Juul was founded by a group of friends who created an e-cigarette that quickly gained widespread popularity, generating over $1 billion in annual revenue. However, it was later revealed that the product had negative health consequences such as addiction and respiratory problems. Despite this knowledge, Juul continued to aggressively market its product to young people, including those who had never smoked before. As a result, a surge in e-cigarette use among youth led to concerns about a potential public health crisis. In response, Juul faced significant legal and regulatory challenges and was accused of contributing to a new generation of nicotine addiction."

# Your Twilio credentials
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = "+18447551091"

def read_phone_numbers(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        return [row[0] for row in csv_reader]

# Read phone numbers from the CSV file
phone_numbers_file = 'phone_numbers.csv'
phone_numbers = read_phone_numbers(phone_numbers_file)


def send_dilemma(phone_number):
    client = Client(account_sid, auth_token)
    time.sleep(1)
    client.messages.create(
        body=dilemma,
        from_=twilio_phone_number,
        to=phone_number
    )

def daily_dilemmas():
    for phone_number in phone_numbers:
        send_dilemma(phone_number)

schedule.every().day.at(DAILY_DILEMMAS_TIME).do(daily_dilemmas)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=run_schedule)
scheduler_thread.start()

@app.route("/sms", methods=["POST"])
def sms_reply():
    phone_number = request.form["From"]
    message_body = request.form["Body"]

    resp = MessagingResponse()

    if message_body.strip().lower() == "done":
        resp.message(outcome)
    else:
        resp.message("Message received. Send 'done' to finish and continue.")

        # Update the user's response in the responses.csv file
        with open('responses.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow([phone_number, dilemma, message_body.strip()])

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, port=5009)
