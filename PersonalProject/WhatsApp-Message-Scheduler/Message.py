import datetime
import json

from Holidays import Holidays


class Message:
    """
    A class representing a message that can be scheduled for a future date and time.

    Attributes:
    - recipient (str): The recipient of the message.
    - message (str): The text of the message.
    - hour (int): The hour of the day when the message should be sent.
    - minute (int): The minute of the hour when the message should be sent.
    - date (str): The date when the message should be sent in the format 'YYYY-MM-DD'.
    - repeat (int): The frequency at which the message should be repeated.
    - repeat_unit (str): The unit of time for the repeat frequency ('n' for none, 'y' for yearly,
    'm' for monthly, 'w' for weekly, 'd' for daily, or 'hol' for on a holiday).
    - holiday (str): The holiday on which the message should be sent. This should be in the format
    'holiday name___country code'.
    """

    def __init__(self, recipient=None, message=None, hour=None, minute=None, date=None, repeat=None, repeat_unit=None,
                 holiday=None, csv_line=None):
        if csv_line is not None:
            self.recipient, self.message, self.hour, self.minute, self.date, self.repeat, self.repeat_unit, self.holiday \
                = ["" if a == "None" else a for a in csv_line.strip().split(',')]
        else:
            if recipient.startswith('0'):
                recipient = '+44' + recipient[1:]

            self.recipient = recipient
            self.message = message
            self.hour = hour
            self.minute = minute
            self.date = date
            self.repeat = repeat
            self.repeat_unit = repeat_unit
            self.holiday = holiday

        if self.date is not None:
            self.formatted_datetime = datetime.datetime.strptime(self.date, '%Y-%m-%d').strftime('%d/%m/%Y')
            if self.hour != "" and self.hour is not None:
                self.formatted_datetime = self.formatted_datetime + " " + f"{self.hour}:{self.minute}"

    def is_old_message(self):
        """
        Check if the current message is old.
        A message is considered old if it is scheduled for a date that has already passed,
        or if it is scheduled for the current date but at a time that has already passed.

        Returns:
            bool: True if the message is old, False otherwise.
        """
        try:
            if self.repeat_unit == "n":
                if self.date is not None:
                    date = datetime.datetime.strptime(self.date + " " + self.hour + ":" + self.minute, '%Y-%m-%d %H:%M')
                    if date < datetime.datetime.now():
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                if datetime.datetime.strptime(self.date, '%Y-%m-%d') < datetime.datetime.now():
                    if self.repeat_unit != "hol":
                        date = self.date.split("-")
                        year = int(date[0])
                        month = int(date[1])
                        day = int(date[2])
                        repeat = int(self.repeat)
                        if self.repeat_unit == "y":
                            self.date = str(datetime.datetime(year + repeat, month, day)).split(" ")[0]
                        elif self.repeat_unit == "m":
                            self.date = str(datetime.datetime(year, month + repeat, day)).split(" ")[0]
                        elif self.repeat_unit == "w":
                            self.date = \
                                str(datetime.datetime(year, month, day) + datetime.timedelta(days=7)).split(" ")[0]
                        elif self.repeat_unit == "d":
                            self.date = str(datetime.datetime(year, month, day + repeat)).split(" ")[0]
                    else:
                        year = int(self.date.split("-")[0])
                        # get current year
                        current_year = datetime.datetime.now().year
                        if year < current_year:
                            year = current_year
                        elif year == current_year:
                            year = current_year + 1

                        holiday_name = self.holiday.split("___")[0]
                        country_code = self.holiday.split("___")[1]
                        holidayObj = Holidays(country_code, year)
                        self.date = holidayObj.get_date_of_holiday(holiday_name)

                return False
        except Exception as e:
            print(e)
            return False

    def make_line(self):
        return f"{self.recipient},{self.message},{self.hour},{self.minute},{self.date},{self.repeat},{self.repeat_unit},{self.holiday}\n"

    def __str__(self):
        return json.dumps(self.__dict__)