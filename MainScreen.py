from functools import partial
import unidecode as uc
import requests
import json
import re
from configparser import *
from pprint import *
from datetime import datetime, timedelta
import concurrent.futures

from kivy.clock import Clock

from WeatherLocation import *
from SpecificWeatherScreen import *
from SettingsScreen import *
from Database import *

from kivy.config import Config
# Due to kivy specification config.set methods need to be called before the remaining kivy import
# and creation of app
config_file = 'configuration/config.ini'
if not os.path.isfile(config_file):
    f = open(config_file, 'w')
    f.write('[Size]\nwindow_size = (1090, 776)\n[Settings]\nnight_hour = 00:00 \nday_hour = 12:00')
    f.close()

config_data = ConfigParser()
config_data.read(config_file, encoding='UTF-8')

try:
    _, width, _, height, _ = re.split(r'\D', config_data['Size'].get('window_size'))
    int(width)
    int(height)
except:
    height = 776
    width = 1090



Config.set('graphics', 'width', width)
Config.set('graphics', 'height', height)
Config.set('kivy', 'window_icon', 'images/icon.ico')

from kivy.app import App
from kivy.loader import Loader
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.lang import Builder

# global variables
city_file = 'configuration/citylist.ini'
city_data = ConfigParser()
city_dict = {}
api_key1 = '8629a0e32c374262b90170540212405'
url_base1 = 'http://api.weatherapi.com/v1/'
api_key2 = '6c1a7de25f36690fa175b834f57e5eef'
url_base2 = 'https://api.openweathermap.org/data/2.5/onecall'
forecast_days = 3

weather_screen = None


class ExistingCity(Exception):
    def __init__(self, argument):
        self.__argument = argument

    def __str__(self):
        return f'{self.__argument} is already added'


# Add City Popup Class
class AddCity(Popup):
    def __init__(self, city_list_layout):
        super(AddCity, self).__init__()
        self.auto_dismiss = False
        self.title = 'Please enter city name'
        self.title_align = 'center'
        self.title_size = 16
        self.title_color = (0, 0, 0, 1)
        self.size_hint = 0.6, 0.3
        self.pos_hint = {"x": 0.2, "y": 0.35}

        self.box1 = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.label = Label(text='', color=(0, 0, 0, 1))
        self.text_input = TextInput(multiline=False)
        self.box2 = BoxLayout(orientation='horizontal', spacing=10)
        self.button1 = Button(text='Apply')
        self.button1.bind(on_press=partial(city_list_layout.add_city, None, self.text_input, self.label, self))
        self.button2 = Button(text='Cancel', on_press=self.dismiss)

        self.add_widget(self.box1)
        self.box1.add_widget(self.label)
        self.box1.add_widget(self.text_input)
        self.box1.add_widget(self.box2)
        self.box2.add_widget(self.button1)
        self.box2.add_widget(self.button2)


# Incorrect City Popup Class
class IncorrectCity(Popup):
    def __init__(self):
        super(IncorrectCity, self).__init__()
        self.auto_dismiss = False
        self.title = 'Some cities are not added'
        self.title_align = 'center'
        self.title_size = 16
        self.title_color = (0, 0, 0, 1)
        self.size_hint = 0.6, 0.175
        self.pos_hint = {"x": 0.2, "y": 0.4125}

        self.box1 = BoxLayout(orientation='horizontal', spacing=10)
        self.button1 = Button(text='Okay')
        self.button1.bind(on_press=self.dismiss)
        self.button2 = Button(text='Show more info', on_press=self.dismiss)

        self.add_widget(self.box1)
        self.box1.add_widget(self.button1)
        self.box1.add_widget(self.button2)


# Confirmation Popup class
class ConfirmationPopup(Popup):
    def __init__(self, msg, func):
        super(ConfirmationPopup, self).__init__()
        self.auto_dismiss = False
        self.title = msg
        self.title_align = 'center'
        self.title_size = 16
        self.title_color = (0, 0, 0, 1)
        self.size_hint = 0.6, 0.175
        self.pos_hint = {"x": 0.2, "y": 0.4125}

        self.box1 = BoxLayout(orientation='horizontal', spacing=10)
        self.button1 = Button(text='Confirm')
        self.button1.bind(on_press=func)
        self.button1.bind(on_press=self.dismiss)
        self.button2 = Button(text='Cancel', on_press=self.dismiss)

        self.add_widget(self.box1)
        self.box1.add_widget(self.button1)
        self.box1.add_widget(self.button2)


# Class displaying weather data
class CityButton(Button):
    delete_mode = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_press(self):
        if self.delete_mode:
            ConfirmationPopup('Are you sure you want to delete city?', self.remove).open()
        else:
            self.change_screen()

    # Opening specific weather screen for chosen city
    def change_screen(self):
        Window.set_system_cursor("wait")
        manager = App.get_running_app().screen_manager
        manager.current = 'Specific weather'
        manager.transition.direction = 'left'
        specific_weather_screen = manager.get_screen('Specific weather')
        specific_weather_screen.ids.specific_city_name.text = self.parent.ids.city_button_name.text
        specific_weather_screen.weather_location = self.parent.weather_location
        specific_weather_screen.night_hour = night_hour
        specific_weather_screen.day_hour = day_hour
        specific_weather_screen.forecast_days = forecast_days
        specific_weather_screen.database = manager.get_screen('City list').database
        specific_weather_screen.create_self()
        Window.set_system_cursor("arrow")

    # Removing self method
    def remove(self, instance):
        par = self.parent
        city_dict.pop(uc.unidecode(par.ids.city_button_name.text))
        par.parent.remove_widget(par)

    # Changing behavior of button
    @classmethod
    def change_behavior(cls, state):
        if state == 'down':
            cls.delete_mode = True
        elif state == 'normal':
            cls.delete_mode = False


# Auxiliary class for CityButton
class CityDisplayer(BoxLayout):
    def __init__(self, weather_location, **kwargs):
        super().__init__(**kwargs)
        self.weather_location = weather_location

    # Update city displayer labels with current data
    def update_labels(self):
        self.ids.city_button_temp_image.source = self.weather_location.current.icon
        self.ids.city_button_temp_image.reload()
        self.ids.city_button_temp_day.text = self.weather_location.current.get_temperature_str()
        self.ids.city_button_temp_night.text = self.weather_location.night.get_temperature_str()


def show_incorrect_city_popup():
    IncorrectCity().open()


class CityListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database = Database()
        self.database.create_database()
        self.incorrect_cities = []
        self.read_cities_file()

    # Reading file and saving cities to city_list
    def read_cities_file(self):
        if not os.path.isfile(city_file):
            f = open(city_file, 'w')
            f.write('[Cities list]\ncities = \n\t')
            f.close()

        global city_data
        city_data = ConfigParser()

        city_data.read(city_file, encoding='UTF-8')
        raw_city_list = city_data['Cities list'].get('cities')
        raw_city_list = raw_city_list.split('\n')

        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #    executor.map(self.add_city, raw_city_list)
        for city in raw_city_list:
            self.add_city(city)

        if self.incorrect_cities:
            # self.show_incorrect_city_popup()
            pass

    # Adding city to city list layout
    def add_city(self, city, text_input=None, label=None, parent=None, instance=None):
        if text_input is not None:
            city = text_input.text

        if city is not None:
            if city != '':
                try:
                    # Api call
                    weather_location = add_weather_city(city)
                    city_name = weather_location.location_polish
                except (IncorrectLocation, NotExistingLocation, ExistingCity) as e:
                    if text_input is None:
                        self.incorrect_cities.append(city)
                    else:
                        label.text = e.__str__()
                else:
                    # Create city displayer and adding to the city layout
                    c = CityDisplayer(weather_location)
                    c.ids.city_button_name.text = city_name
                    c.update_labels()
                    self.ids.city_layout.add_widget(c)
                    self.database.insert_weather(weather_location)
                    if parent is not None:
                        parent.dismiss()

    def show_city_popup(self):
        AddCity(self).open()

    # Removing the city
    def remove_city(self):
        CityButton.change_behavior(self.ids.remove_city.state)

    # Refreshing cities in city layout
    def refresh_city_layout(self, spinner=None, value=None):
        Window.set_system_cursor("wait")
        if value is not None:
            global night_hour
            night_hour = value

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(update_weather, self.ids.city_layout.children)
        Window.set_system_cursor("arrow")

    # Apply change of day hour
    def change_day_hour(self, spinner=None, value=None):
        if value is not None:
            global day_hour
            day_hour = value

    # On press remove button
    def change_rem_image(self):
        if self.ids.remove_city.state == 'down':
            self.ids.remove_city_image.source = 'images/remove_down.png'
        if self.ids.remove_city.state == 'normal':
            self.ids.remove_city_image.source = 'images/remove_up.png'

# App class
class WeatherViewer(App):
    def build(self):
        Window.minimum_height = 776
        Window.minimum_width = 1090

        self.read_config_file()
        Window.bind(on_request_close=self.on_request_close)

        # Creating screen manager
        self.screen_manager = ScreenManager(transition=SlideTransition())

        # Adding screens
        city_list_screen = CityListScreen()
        self.screen_manager.add_widget(city_list_screen)
        settings_screen = SettingsScreen()
        settings_screen.ids.night_hour_spinner.text = night_hour
        settings_screen.ids.night_hour_spinner.bind(text=city_list_screen.refresh_city_layout)
        settings_screen.ids.day_hour_spinner.text = day_hour
        settings_screen.ids.day_hour_spinner.bind(text=city_list_screen.change_day_hour)
        self.screen_manager.add_widget(settings_screen)
        self.screen_manager.add_widget(SpecificWeatherScreen())

        self.update_date()
        Clock.schedule_interval(self.update_date, 60)
        return self.screen_manager

    def screen_manager(self):
        return self.screen_manager

    # Updating data in labels
    def update_date(self, *args):
        today_date = datetime.today().strftime('%Y-%m-%d %H:%M')
        self.screen_manager.get_screen('Specific weather').ids.specific_city_date.text = today_date
        self.screen_manager.get_screen('City list').ids.city_list_date.text = today_date


    # Reading data from config file
    def read_config_file(self):
        # config_data.read(config_file, encoding='UTF-8')
        global night_hour
        night_hour = config_data['Settings'].get('night_hour')
        global day_hour
        day_hour = config_data['Settings'].get('day_hour')

        try:
            datetime.strptime(night_hour, '%H:%M')
        except ValueError:
            night_hour = '00:00'

        try:
            datetime.strptime(day_hour, '%H:%M')
        except ValueError:
            day_hour = '12:00'

    def on_request_close(self, *args):
        ConfirmationPopup('Are you sure you want to exit?', self.end_of_work).open()
        return True

    # Method saving data in config file
    def end_of_work(self, instance):
        if city_dict:
            city_string = '\n'

            for city in city_dict:
                city_string += city_dict.get(city).location_polish
                city_string += '\n'

            city_data['Cities list']['cities'] = city_string
            with open(city_file, 'w', encoding='UTF-8') as config:
                city_data.write(config)

        config_data['Size']['window_size'] = str(Window.size)
        config_data['Settings']['night_hour'] = night_hour
        config_data['Settings']['day_hour'] = day_hour
        with open(config_file, 'w', encoding='UTF-8') as config:
            config_data.write(config)

        self.stop()


# Getting data for city and creating WeatherLocation object
def add_weather_city(city_name, is_new=True):
    city_name_decoded = uc.unidecode(city_name)
    payload = {'key': api_key1, 'q': city_name_decoded, 'days': forecast_days}
    request = requests.get(url_base1 + 'forecast.json', params=payload)

    if is_new:
        if city_name_decoded in city_dict:
            raise ExistingCity(city_name)
        else:
            weather_location = WeatherLocation.create_from_json(request.json(), city_name, night_hour, forecast_days)
            city_dict.update({city_name_decoded: weather_location})

        return weather_location
    else:
        weather_location = city_dict.get(city_name_decoded)
        weather_location.update_current(request.json())
        weather_location.update_night(request.json(), night_hour)
        city_dict.update({city_name_decoded: weather_location})

        return weather_location
    pass


# Updating city displayer weather
def update_weather(city_displayer):
    city_name = city_displayer.ids.city_button_name.text
    weather_location = add_weather_city(city_name, is_new=False)

    city_displayer.weather_location = weather_location
    city_displayer.update_labels()
    pass
