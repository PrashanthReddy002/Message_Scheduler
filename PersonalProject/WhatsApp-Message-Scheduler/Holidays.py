import json
import os

import requests


class Holidays:
    def __init__(self, country_code, year):
        """
        :param country_code: The ISO 3166-1 alpha-2 country code of the country to get the holidays for (e.g. "GB" for the United Kingdom)
        :param year: The year to get the holidays for.
        """
        self.API_KEY = open("data/calendarific_api_key.dat", "r").read()
        self.country_code = country_code
        self.year = year
        self.holidays = None

    def get_holidays(self):
        """
        Returns a list of holidays for the given country code and year.
        :return: A JSON response containing the holidays with the following format:
            {
               "date":"2023-01-01",
               "localName":"New Year\\'s Day",
               "name":"New Year\\'s Day",
               "countryCode":"GB",
               "fixed":false,
               "global":false,
               "counties":[
                  "GB-NIR"
               ],
               "launchYear":null,
               "types":[
                  "Public"
               ]
            }
        """

        # Check if json already exists as a file
        # If it does, load it
        if os.path.exists(f"{self.country_code}_{self.year}.json"):
            with open(f"data/{self.country_code}_{self.year}.json", 'r') as f:
                self.holidays = json.load(f)
        else:
            if len(self.country_code) != 2:
                return None

            url = f"https://calendarific.com/api/v2/holidays?&api_key={self.API_KEY}&country={self.country_code}&year={self.year}"
            response = requests.get(url)
            self.holidays = response.json()
            if response.status_code != 200:
                return None
            # Save json to file
            with open(f"data/{self.country_code}_{self.year}.json", 'w') as f:
                json.dump(self.holidays, f)
        return self.holidays

    def get_holiday_names_list(self):
        """
        Returns a list of holiday names for the given country code and year.
        :return: A list of holiday names
        """
        if self.holidays is None:
            holidays = self.get_holidays()
            if holidays is None:
                return None
            self.holidays = self.get_holidays()
        holiday_names = []
        for holiday in self.holidays['response']['holidays']:
            holiday_names.append(holiday['name'])
        return holiday_names

    def get_holiday_dates(self, country_code, year):
        """
        Returns a list of holiday dates for the given country code and year.
        :param country_code: The ISO 3166-1 alpha-2 country code of the country to get the holidays for (e.g. "GB" for the United Kingdom)
        :param year: The year to get the holidays for.
        :return: A list of holiday dates in the format "YYYY-MM-DD"
        """
        if self.holidays is None:
            if self.holidays is None:
                holidays = self.get_holidays()
                if holidays is None:
                    return None

        holiday_dates = []
        for holiday in self.holidays['response']['holidays']:
            holiday_dates.append(holiday['date']['iso'])
        return holiday_dates

    def get_date_of_holiday(self, holiday_name):
        """
        Returns the date of the given holiday in the given country and year.
        :param holiday_name: The name of the holiday to get the date for.
        :return: A date in the format "YYYY-MM-DD"
        """
        if self.holidays is None:
            if self.holidays is None:
                holidays = self.get_holidays()
                if holidays is None:
                    return None
        for holiday in self.holidays['response']['holidays']:
            if holiday['name'] == holiday_name:
                return holiday['date']['iso']
        return None
