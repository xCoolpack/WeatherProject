from WeatherHourly import *
import unidecode as uc

from pprint import pprint

class IncorrectLocation(Exception):
    def __init__(self, argument):
        self.__argument = argument

    def __str__(self):
        return f'{self.__argument} is not located in Poland'


class NotExistingLocation(Exception):
    def __init__(self, argument):
        self.__argument = argument

    def __str__(self):
        return f'{self.__argument} does not exist'


# Class contains weather for location
class WeatherLocation:
    def __init__(self, city_name, location, night_hour='00:00', days=None, current=None, forecast=None, hourly_list=None):
        if location is not None:
            self.set_location(location, city_name)

            self.__hourly = []
            if current is not None or forecast is not None:
                self.set_current(current, location)
                self.set_night(forecast, night_hour)
                self.set_hourly_from_forecast(forecast, days)
            else:
                self.__current = None
                self.__night = None
                self.set_hourly(hourly_list)
        else:
            raise NotExistingLocation(city_name)

    @property
    def location(self):
        return self.__location

    @property
    def location_polish(self):
        return self.__location_polish

    @property
    def coordinate(self):
        return self.__coordinate

    def set_location(self, location, city_name):
        if type(location) == dict:
            if location.get('country') != 'Poland':
                raise IncorrectLocation(location.get('name'))
            else:
                self.__location = location.get('name')
                self.__location_polish = city_name.capitalize()
                self.__coordinate = (float(location.get('lat')), float(location.get('lon')))
        else:
            self.__location = uc.unidecode(city_name).capitalize()
            self.__location_polish = city_name.capitalize()

    @property
    def current(self):
        return self.__current

    def set_current(self, current, location):
        date = location.get('localtime').split()[1]
        self.__current = WeatherHourly.create_from_json(date, current)

    def update_current(self, forecast_data):
        current = forecast_data.get('current')
        location = forecast_data.get('location')
        date = location.get('localtime').split()[1]
        self.__current = WeatherHourly.create_from_json(date, current)

    @property
    def night(self):
        return self.__night

    def set_night(self, forecast, night_hour):
        hourly_list = forecast.get('forecastday')[check_time(night_hour)].get('hour')
        date = ''
        for hour in hourly_list:
            if hour.get('time').split(' ')[1] == night_hour:
                forecast = hour
                date = hour.get('time')

        self.__night = WeatherHourly.create_from_json(date, forecast)

    def update_night(self, forecast_data, night_hour):
        forecast = forecast_data.get('forecast')
        hourly_list = forecast.get('forecastday')[check_time(night_hour)].get('hour')
        date = ''
        for hour in hourly_list:
            if hour.get('time').split(' ')[1] == night_hour:
                forecast = hour
                date = hour.get('time')

        self.__night = WeatherHourly.create_from_json(date, forecast)

    @property
    def hourly(self):
        return self.__hourly

    # Create new hourly forecasts and appends to the lists
    def set_hourly_from_forecast(self, forecast, days):
        for i in range(days):
            hourly_list = forecast.get('forecastday')[i].get('hour')
            for hour in hourly_list:
                forecast_ = hour
                date = hour.get('time')
                self.__hourly.append(WeatherHourly.create_from_json(date, forecast_))

    # Appending hourly forecasts to the list
    def set_hourly(self, hourly_list):
        for hour in hourly_list:
            weather_hourly = WeatherHourly.create_from_database(hour)
            self.__hourly.append(weather_hourly)

    def print_hourly(self):
        for hour in self.__hourly:
            print(hour)

    # Constructor creating object from json
    @classmethod
    def create_from_json(cls, forecast_data, city_name, night_hour, days):
        current = forecast_data.get('current')
        forecast = forecast_data.get('forecast')
        location = forecast_data.get('location')

        return cls(city_name, location, night_hour, days, current=current, forecast=forecast)

    # Constructor creating object from database
    @classmethod
    def create_from_database(cls, city_name, hourly_list):
        return cls(city_name, 'Database', hourly_list=hourly_list)

    def __str__(self):
        return f'{self.__location_polish}:\n{self.__current}\n{self.__night}'

    def __repr__(self):
        return f'{self.__location_polish}:\n{self.__current}'


def check_time(hour):
    hour, _ = hour.split(':')
    if int(hour) < 8:
        return 1
    else:
        return 0
