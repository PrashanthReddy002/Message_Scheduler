import datetime

import pyautogui

import MessageSender


def within_time(message, loop_buffer=2, message_send_buffer=50):
    # Get timestamp of message

    message_timestamp = datetime.datetime.strptime(f"{message.date} {message.hour}:{message.minute}",
                                                   "%Y-%m-%d %H:%M")

    # Get timestamp of now
    now_timestamp = datetime.datetime.now()

    return message_timestamp >= now_timestamp - datetime.timedelta(seconds=message_send_buffer + loop_buffer) and not (message_timestamp >= now_timestamp)


def prepare_string_for_url(message_string):
    # Make sure the message is a string
    message_string = str(message_string)

    # Replace spaces with %20
    message_string = message_string.replace(" ", "%20")

    return message_string


def get_coord(percent_x, percent_y):
    WIDTH, HEIGHT = pyautogui.size()

    x = (WIDTH / 100) * percent_x
    y = (HEIGHT / 100) * percent_y

    return x, y
