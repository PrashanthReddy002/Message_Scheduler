import atexit
import csv
import datetime
import hashlib
import os
import random
import threading
import time
import webbrowser as web

import pyautogui

import Utils

import pywhatkit as kit

from Message import Message

class MessageSender:
    def __init__(self, messages_file):
        self.message_send_buffer = 50
        self.thread = None
        self.is_running = True
        self.hash_of_file = None
        self.messages_file = messages_file
        self.messages = []

        # If messages_file does not exist, create it
        if not os.path.exists(self.messages_file):
            f = open(self.messages_file, "w")
            f.close()

        # # Read the messages from the CSV file
        self.read_messages_from_csv()
        self.delete_old_messages()

        if os.path.exists(os.path.join("static", "contacts.csv")):
            self.csv_validator(os.path.join("static", "contacts.csv"))
            self.add_sequential_id_to_csv(os.path.join("static", "contacts.csv"))

        if os.path.exists(os.path.join("static", "groups.csv")):
            self.csv_validator(os.path.join("static", "groups.csv"))
            self.add_sequential_id_to_csv(os.path.join("static", "groups.csv"))


    def read_messages_from_csv(self):
        print("Reading messages from CSV file...")
        # Open the CSV file in read mode
        with open(self.messages_file, 'r', encoding='UTF-8') as f:
            # Create an empty list to store the new lines
            new_lines = []

            # Iterate through the lines in the CSV file
            for line in f:
                if len(line) > 5:
                    # Create a message object for the line
                    message = Message(csv_line=line)

                    # If the message is not an old message, add the line to the list of new lines
                    if not message.is_old_message():
                        self.messages.append(message)
                        new_lines.append(message.make_line())
                    else:
                        print("Skipping old message:", message)
        # Open the CSV file in write mode and overwrite the file with the new lines
        with open(self.messages_file, 'w', encoding='UTF-8') as f:
            f.writelines(new_lines)
        print("Done.")

    def add_sequential_id_to_csv(self, csv_file):
        try:
            with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)

            header = rows[0]
            id_column_index = None

            # Check if 'ID' column exists, if not, add it
            if 'ID' not in header:
                header.append('ID')
                id_column_index = len(header) - 1
            else:
                id_column_index = header.index('ID')

            # Add a sequential ID to each row
            if id_column_index is not None:
                for i, row in enumerate(rows[1:], start=1):
                    if len(row) <= id_column_index:
                        row.extend([''] * (id_column_index - len(row) + 1))
                    if not row[id_column_index]:
                        row[id_column_index] = str(i)

            # Write the modified data back to the CSV file
            with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(rows)

        except Exception as e:
            print("Error:", e)

    def csv_validator(self, input_file_path):
        clean_rows = []

        with open(input_file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                clean_rows.append(row)

        # Checking if the file has any content
        if not clean_rows:
            print("The file is empty.")
            return

        # Assuming the first row is the header
        header = clean_rows[0]
        expected_columns = len(header)

        # Validate and adjust each row
        corrected_lines = []
        for row in clean_rows:
            if len(row) < expected_columns:
                # Add missing columns
                row += [''] * (expected_columns - len(row))
            elif len(row) > expected_columns:
                # Truncate extra columns
                row = row[:expected_columns]

            corrected_lines.append(row)

        # Write the corrected data back to the file
        with open(input_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(corrected_lines)


    def get_messages(self):
        messages = []
        self.read_messages_from_csv()
        for message_info in self.messages:
            if not message_info.is_old_message():
                messages.append(message_info)
        return sorted(messages, key=lambda message: message.date)

    def add_message(self, recipient, message, hour=None, minute=None, date=None, repeat=None, repeat_unit=None,
                    holiday_name=None):
        new_message = Message(recipient, message, hour, minute, date, repeat, repeat_unit)
        self.messages.append(new_message)

        # Save message to file
        with open(self.messages_file, 'a', encoding='UTF-8') as f:
            f.write(f"{recipient},{message},{hour},{minute},{date},{repeat},{repeat_unit},{holiday_name}\n")


    def delete_old_messages(self):
        # Open the CSV file in read mode
        with open(self.messages_file, 'r', encoding='UTF-8') as f:
            # Create an empty list to store the new lines
            new_lines = []

            # Iterate through the lines in the CSV file
            for line in f:
                if len(line) > 5:
                    # Create a message object for the line
                    message = Message(csv_line=line)

                    # If the message is not an old message, add the line to the list of new lines
                    if not message.is_old_message():
                        new_lines.append(message.make_line())

        # Open the CSV file in write mode and overwrite the file with the new lines
        with open(self.messages_file, 'w', encoding='UTF-8') as f:
            f.writelines(new_lines)

    def _has_message_file_changed(self):
        hash_of_file = hashlib.md5(open(self.messages_file, 'rb').read()).hexdigest()
        output = False

        if self.hash_of_file != hash_of_file:
            output = True
            self.hash_of_file = hash_of_file
        return output

    @staticmethod
    def sendwhatmsg_instantly(
            phone_no: str,
            message: str,
            wait_time: int = 15
    ) -> None:
        """
        Send WhatsApp Message Instantly

        Taken and modified from pywhatkit https://github.com/Ankit404butfound/PyWhatKit
        """

        # Prepare message for URL
        message = Utils.prepare_string_for_url(message)

        web.open(f"https://web.whatsapp.com/send?phone={phone_no}&text={message}")

        time.sleep(2)

        pyautogui.press("F11")

        time.sleep(4)

        time.sleep(wait_time - 4)

        # 61.66666666666667%, 95.0%
        x, y = Utils.get_coord(61.66666666666667, 95.0)
        pyautogui.click(x, y)

        pyautogui.press("enter")

    @staticmethod
    def send_another(recipient, message_string):
        # Coordinates where the mouse will click
        # %, %
        x, y = Utils.get_coord(15.416666666666668, 12.314814814814815)

        # Move the mouse to the specified coordinates
        pyautogui.moveTo(x, y)

        # Click at the current mouse location
        pyautogui.click()

        # Wait a moment for any window or field to activate
        time.sleep(1)

        # Type phone number
        pyautogui.write(recipient)

        time.sleep(1)

        x, y = Utils.get_coord(16.40625, 27.777777777777775)
        # Click the contact
        pyautogui.moveTo(x, y)

        pyautogui.click()

        time.sleep(1)

        pyautogui.write(message_string)

        pyautogui.press("enter")

    def send_messages(self):
        wait_time = 10
        while self.is_running:
            if self._has_message_file_changed():
                self.read_messages_from_csv()
                self.delete_old_messages()
                self.messages = self.get_messages()

            now_messages = [message for message in self.messages if Utils.within_time(message, wait_time, self.message_send_buffer)]

            for message in now_messages:
                # if first message
                if message == now_messages[0]:
                    # Send the message
                    self.sendwhatmsg_instantly(message.recipient, message.message, self.message_send_buffer)
                    time.sleep(1)
                else:
                    self.send_another(message.recipient, message.message)
                    time.sleep(1)
            self.delete_old_messages()
            if len(now_messages) > 0:
                pyautogui.hotkey("ctrl", "w")
            time.sleep(wait_time)

    def start(self):
        self.thread = threading.Thread(target=self.send_messages)
        self.thread.daemon = True
        self.thread.start()

    def stop_thread(self):
        self.is_running = False


if __name__ == "__main__":
    # Create messages.txt file if it doesn't exist
    if not os.path.exists('messages.txt'):
        open('messages.txt', 'w').close()

    messageSender = MessageSender('messages.txt')
    messageSender.start_thread()
