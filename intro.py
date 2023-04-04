import os
import csv
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

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

# Your introduction message
intro_message = (
    "Hey, this is Christian, Dom, Jose, and Santiago. Thanks for signing up to the first MVP of the Introspect Chatbot. Every day, Introspect will send you an ethical dilemma. "
    "Reply with what you would do as a daily exercise for yourself. When finished, type 'done' at the next message. "
    "We will store your answers so that you can come back to them in the future. "
    "We hope that this exercise will help you introspect about your values and encourage you to do good in the world."
)

def send_intro_message(phone_number):
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=intro_message,
        from_=twilio_phone_number,
        to=phone_number
    )

def send_intro_messages():
    for phone_number in phone_numbers:
        send_intro_message(phone_number)

if __name__ == "__main__":
    send_intro_messages()
