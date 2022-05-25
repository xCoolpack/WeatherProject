import datetime
import os
import sqlite3
import re
from datetime import datetime, timedelta

from WeatherLocation import *
from WeatherHourly import *


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None


class Database:
    city_list = []

    def __init__(self):
        self.filename = 'data/weather_database.db'
        self.create = not os.path.exists(self.filename)
        self.conn = sqlite3.connect(self.filename)
        self.conn.create_function("REGEXP", 2, regexp)

    # Create database tables
    def create_database(self):
        if self.create:
            c = self.conn.cursor()

            # Create location table for WeatherLocation
            c.execute('''CREATE TABLE Locations (
                      Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                      Location TEXT NOT NULL,
                      Date TEXT NOT NULL
                      )''')

            # Create weather_forecasts table for WeatherHourly
            c.execute('''CREATE TABLE Forecasts (
                      Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                      Time TEXT NOT NULL,
                      Temperature REAL NOT NULL,
                      Wind_velocity REAL NOT NULL,
                      Wind_direction TEXT NOT NULL,
                      Precipitation REAL NOT NULL,
                      Pressure REAL NOT NULL,
                      Humidity INTEGER NOT NULL,
                      Cloudiness INTEGER NOT NULL,
                      Id_locations INTEGER NOT NULL,
                      FOREIGN KEY (Id_locations) REFERENCES locations
                      )''')
            self.conn.commit()

    # Insert WeatherLocation and/or WeatherHourly
    def insert_weather(self, weather_location):
        c = self.conn.cursor()
        city_name = weather_location.location
        today = datetime.today().strftime('%Y-%m-%d')

        c.execute(f"""SELECT * FROM Locations WHERE Location='{city_name}' AND
                  Date='{today}'""")

        result = c.fetchall()
        self.conn.commit()

        if not result:
            c.execute("""INSERT INTO Locations (Location, Date) VALUES (?, ?)""", (city_name, today))
            self.conn.commit()

            c.execute(f"""SELECT * FROM Locations WHERE Location='{city_name}' AND Date='{today}'""")
            location_id = c.fetchone()[0]
            weather_hourly_list = weather_location.hourly

            for weather in weather_hourly_list:
                c.execute("""INSERT INTO Forecasts (Time, Temperature, Wind_velocity, Wind_direction, Precipitation, 
                          Pressure, Humidity, Cloudiness, Id_locations) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                          weather.get_tuple(location_id))
                self.conn.commit()

            c.execute(f"""SELECT * FROM Forecasts WHERE Id_locations='{location_id}'""")

    def get_weather_history(self, city_name, today_date, days):
        def create_weather_location(today, date):
            c.execute(f"""SELECT * FROM Locations WHERE Location='{city_name}' AND Date='{date}'""")
            location_id = c.fetchone()
            if location_id is not None:
                location_id = location_id[0]

                c.execute(f"""SELECT * FROM Forecasts WHERE Time REGEXP '{today}' AND Id_locations='{location_id}'""")
                hourly_list = c.fetchall()

                return WeatherLocation.create_from_database(city_name, hourly_list)
            return None

        c = self.conn.cursor()

        weather_location_list = []

        if days > 1:
            for i in range(1, days):
                weather_location_list.append(
                    create_weather_location(today_date.strftime('%Y-%m-%d'),
                                            (today_date - timedelta(days=i)).strftime('%Y-%m-%d')))

        return weather_location_list

    def clear_tables(self):
        c = self.conn.cursor()

        c.execute("""DELETE FROM Locations""")
        c.execute("""DELETE FROM Forecasts""")
        self.conn.commit()

        c.execute(f"""SELECT * FROM Locations""")
        pprint(c.fetchall())


if __name__ == '__main__':
    pass
