import datetime
import json

from flask import Flask, request, render_template

from Holidays import Holidays
from MessageSender import MessageSender

app = Flask(__name__)


@app.route("/")
def index():
    print("index")
    # Get the list of messages from the MessageSender instance
    messages = message_sender.get_messages()

    # Render the HTML template with the list of messages
    return render_template("index.html", messages=messages)


@app.route("/add", methods=["POST"])
def add_message():
    # Get the message data from the request form
    recipients = request.form.getlist('recipient[]')
    recipients = [a for a in recipients if a != '']
    print(recipients)
    message = request.form.get("message")

    time = request.form.get("time")

    if time != "":
        time = time.split(":")
        hour = time[0]
        minute = time[1]
    else:
        hour = None
        minute = None

    date = request.form.get("date")
    repeat = request.form.get("repeat")
    repeat_unit = request.form.get("repeat_unit")

    holiday_name = request.form.get("holiday")
    country_code = request.form.get("country-code")

    if holiday_name != "":
        holiday = f"{holiday_name}___{country_code}"
    else:
        holiday = None

    # Add the message to the MessageSender instance
    for recipient in recipients:
        message_sender.add_message(recipient, message, hour, minute, date, repeat, repeat_unit,
                                   holiday)

    return "Message added", 201


@app.route("/holidays", methods=["GET"])
def get_holiday_names():
    country_code = request.args.get("country_code")
    year = datetime.datetime.now().year
    holidays = Holidays(country_code, year)
    return json.dumps(holidays.get_holiday_names_list()), 200

@app.route("/holiday_date", methods=["GET"])
def get_holiday_name():
    country_code = request.args.get("country_code")
    holiday_name = request.args.get("holiday")
    if country_code is None or holiday_name is None:
        error_message = ["country_code" if country_code is None else "", "holiday" if holiday_name is None else ""]
        return "Missing parameter" + ",".join(error_message), 400

    year = datetime.datetime.now().year
    holidays = Holidays(country_code, year)
    print(holiday_name)
    holiday_date = holidays.get_date_of_holiday(holiday_name)
    # Is holiday date in the past?
    if datetime.datetime.strptime(holiday_date, '%Y-%m-%d') < datetime.datetime.now():
        # Get the date of the holiday next year
        holiday_date = holidays.get_date_of_holiday(holiday_name, year + 1)
    return holiday_date, 200


if __name__ == "__main__":
    # Create a MessageSender instance
    message_sender = MessageSender("messages.txt")

    message_sender.start()

    print("Starting Flask app")
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
