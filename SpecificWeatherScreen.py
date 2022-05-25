import concurrent.futures
import re
from datetime import datetime, timedelta
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image, AsyncImage
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

from Database import *

hours_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
              '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21',
              '22', '23']


# Chart class
class Chart(AsyncImage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.weather_location_hourly = None
        self.size_hint = 1, 1
        self.keep_ratio: True
        self.allow_stretch: True

    # Setting chart for today's data
    def set_today_chart(self, data_type):
        filename = 'charts/today' + data_type + '.png'
        values = []
        measure = ''

        if data_type == 'Temperature':
            measure = ' [\xb0C]'
            for weather_hour in self.weather_location_hourly:
                if re.match(datetime.today().strftime('%Y-%m-%d'), weather_hour.time):
                    values.append(weather_hour.temperature)
        elif data_type == 'Wind':
            measure = ' [km/h]'
            for weather_hour in self.weather_location_hourly:
                if re.match(datetime.today().strftime('%Y-%m-%d'), weather_hour.time):
                    values.append(weather_hour.wind_velocity)
        elif data_type == 'Precipitation':
            measure = ' [mm]'
            for weather_hour in self.weather_location_hourly:
                if re.match(datetime.today().strftime('%Y-%m-%d'), weather_hour.time):
                    values.append(weather_hour.precipitation)
        elif data_type == 'Humidity':
            measure = ' [%]'
            for weather_hour in self.weather_location_hourly:
                if re.match(datetime.today().strftime('%Y-%m-%d'), weather_hour.time):
                    values.append(weather_hour.humidity)
        elif data_type == 'Cloudiness':
            measure = ' [%]'
            for weather_hour in self.weather_location_hourly:
                if re.match(datetime.today().strftime('%Y-%m-%d'), weather_hour.time):
                    values.append(weather_hour.cloudiness)
        elif data_type == 'Pressure':
            measure = ' [Mb]'
            for weather_hour in self.weather_location_hourly:
                if re.match(datetime.today().strftime('%Y-%m-%d'), weather_hour.time):
                    values.append(weather_hour.pressure_mb)
        colors = []
        curr_hour = datetime.today().strftime('%H')
        for hour in hours_list:
            if hour == curr_hour or '0' + hour == curr_hour:
                colors.append('darkorange')
            else:
                colors.append('steelblue')

        plt.figure(figsize=(16, 8))
        plt.bar(hours_list, values, width=0.6, color=colors)

        plt.xlabel('Hour')
        plt.ylabel(data_type + measure)
        if data_type == 'Pressure':
            plt.ylim([975, 1050])
        elif data_type == 'Precipitation':
            plt.ylim(0)

        for i in range(len(values)):
            plt.annotate(str(values[i]), xy=(hours_list[i], values[i]), ha='center', va='bottom')

        plt.savefig(filename)
        plt.close()

        self.source = ''
        self.source = filename
        self.reload()

    # Setting chart for forecast data
    def set_forecast_chart(self, data_type, forecast_days):
        filename = 'charts/forecast' + data_type + '.png'
        day_hour = App.get_running_app().screen_manager.current_screen.day_hour
        night_hour = App.get_running_app().screen_manager.current_screen.night_hour

        values_day = []
        values_night = []
        measure = ''
        dates = []

        for i in range(forecast_days):
            dates.append((datetime.today() - timedelta(days=i * -1)).strftime('%Y-%m-%d'))
        index_d = 0
        index_n = 0

        if data_type == 'Temperature':
            measure = ' [\xb0C]'
            for weather_hour in self.weather_location_hourly:
                if index_d < 3 and re.match(dates[index_d] + ' ' + day_hour, weather_hour.time):
                    values_day.append(weather_hour.temperature)
                    index_d += 1
                elif index_n < 3 and re.match(dates[index_n] + ' ' + night_hour, weather_hour.time):
                    values_night.append(weather_hour.temperature)
                    index_n += 1
        elif data_type == 'Wind':
            measure = ' [km/h]'
            for weather_hour in self.weather_location_hourly:
                if index_d < 3 and re.match(dates[index_d] + ' ' + day_hour, weather_hour.time):
                    values_day.append(weather_hour.wind_velocity)
                    index_d += 1
                elif index_n < 3 and re.match(dates[index_n] + ' ' + night_hour, weather_hour.time):
                    values_night.append(weather_hour.wind_velocity)
                    index_n += 1
        elif data_type == 'Precipitation':
            measure = ' [mm]'
            for weather_hour in self.weather_location_hourly:
                if index_d < 3 and re.match(dates[index_d] + ' ' + day_hour, weather_hour.time):
                    values_day.append(weather_hour.precipitation)
                    index_d += 1
                elif index_n < 3 and re.match(dates[index_n] + ' ' + night_hour, weather_hour.time):
                    values_night.append(weather_hour.precipitation)
                    index_n += 1
        elif data_type == 'Humidity':
            measure = ' [%]'
            for weather_hour in self.weather_location_hourly:
                if index_d < 3 and re.match(dates[index_d] + ' ' + day_hour, weather_hour.time):
                    values_day.append(weather_hour.humidity)
                    index_d += 1
                elif index_n < 3 and re.match(dates[index_n] + ' ' + night_hour, weather_hour.time):
                    values_night.append(weather_hour.humidity)
                    index_n += 1
        elif data_type == 'Cloudiness':
            measure = ' [%]'
            for weather_hour in self.weather_location_hourly:
                if index_d < 3 and re.match(dates[index_d] + ' ' + day_hour, weather_hour.time):
                    values_day.append(weather_hour.cloudiness)
                    index_d += 1
                elif index_n < 3 and re.match(dates[index_n] + ' ' + night_hour, weather_hour.time):
                    values_night.append(weather_hour.cloudiness)
                    index_n += 1
        elif data_type == 'Pressure':
            measure = ' [Mb]'
            for weather_hour in self.weather_location_hourly:
                if index_d < 3 and re.match(dates[index_d] + ' ' + day_hour, weather_hour.time):
                    values_day.append(weather_hour.pressure_mb)
                    index_d += 1
                elif index_n < 3 and re.match(dates[index_n] + ' ' + night_hour, weather_hour.time):
                    values_night.append(weather_hour.pressure_mb)
                    index_n += 1

        plt.figure(figsize=(16, 8))
        width = 0.075
        x = np.arange(len(dates))

        plt.bar(x - width / 2, values_day, width, color='steelblue', label='day')
        plt.bar(x + width / 2, values_night, width, color='darkorange', label='night')

        plt.xlabel('Date')
        plt.ylabel(data_type + measure)
        if data_type == 'Pressure':
            plt.ylim([975, 1050])
        elif data_type == 'Precipitation':
            plt.ylim(0)

        for i in range(len(values_day)):
            plt.annotate(str(values_day[i]), xy=(x[i], values_day[i]), ha='right', va='bottom')
            plt.annotate(str(values_night[i]), xy=(x[i], values_night[i]), ha='left', va='bottom')

        plt.legend()
        plt.xticks(ticks=x, labels=dates)

        plt.savefig(filename)
        plt.close()

        self.source = ''
        self.source = filename
        self.reload()

    # Setting chart for forecasts diffrences data
    def set_forecast_diff_chart(self, data_type, forecast_days):
        filename = 'charts/forecast_diff' + data_type + '.png'
        measure = ''
        city_name = App.get_running_app().screen_manager.current_screen.weather_location.location
        db = App.get_running_app().screen_manager.current_screen.database
        weather_location_yesterday, weather_location_day_before_yesterday = db.get_weather_history(city_name,
                                                                                                   datetime.today(),
                                                                                                   forecast_days)
        values_today = []
        values_yesterday = []
        values_day_before_yesterday = []

        if data_type == 'Temperature':
            measure = ' [\xb0C]'
            if weather_location_yesterday is not None:
                for i in range(len(weather_location_yesterday.hourly)):
                    values_yesterday.append(weather_location_yesterday.hourly[i].temperature)
                    if weather_location_day_before_yesterday is not None:
                        values_day_before_yesterday.append(weather_location_day_before_yesterday.hourly[i].temperature)
            for weather_hour in self.weather_location_hourly:
                if re.match(datetime.today().strftime('%Y-%m-%d'), weather_hour.time):
                    values_today.append(weather_hour.temperature)
        elif data_type == 'Wind':
            measure = ' [km/h]'
            if weather_location_yesterday is not None:
                for i in range(len(weather_location_yesterday.hourly)):
                    values_yesterday.append(weather_location_yesterday.hourly[i].wind_velocity)
                    if weather_location_day_before_yesterday is not None:
                        values_day_before_yesterday.append(weather_location_day_before_yesterday.hourly[i].wind_velocity)
            for weather_hour in self.weather_location_hourly:
                if re.match(datetime.today().strftime('%Y-%m-%d'), weather_hour.time):
                    values_today.append(weather_hour.wind_velocity)
        elif data_type == 'Precipitation':
            measure = ' [mm]'
            if weather_location_yesterday is not None:
                for i in range(len(weather_location_yesterday.hourly)):
                    values_yesterday.append(weather_location_yesterday.hourly[i].precipitation)
                    if weather_location_day_before_yesterday is not None:
                        values_day_before_yesterday.append(weather_location_day_before_yesterday.hourly[i].precipitation)
            for weather_hour in self.weather_location_hourly:
                if re.match(datetime.today().strftime('%Y-%m-%d'), weather_hour.time):
                    values_today.append(weather_hour.precipitation)
        elif data_type == 'Humidity':
            measure = ' [%]'
            if weather_location_yesterday is not None:
                for i in range(len(weather_location_yesterday.hourly)):
                    values_yesterday.append(weather_location_yesterday.hourly[i].humidity)
                    if weather_location_day_before_yesterday is not None:
                        values_day_before_yesterday.append(weather_location_day_before_yesterday.hourly[i].humidity)
            for weather_hour in self.weather_location_hourly:
                if re.match(datetime.today().strftime('%Y-%m-%d'), weather_hour.time):
                    values_today.append(weather_hour.humidity)
        elif data_type == 'Cloudiness':
            measure = ' [%]'
            if weather_location_yesterday is not None:
                for i in range(len(weather_location_yesterday.hourly)):
                    values_yesterday.append(weather_location_yesterday.hourly[i].cloudiness)
                    if weather_location_day_before_yesterday is not None:
                        values_day_before_yesterday.append(weather_location_day_before_yesterday.hourly[i].cloudiness)
            for weather_hour in self.weather_location_hourly:
                if re.match(datetime.today().strftime('%Y-%m-%d'), weather_hour.time):
                    values_today.append(weather_hour.cloudiness)
        elif data_type == 'Pressure':
            measure = ' [Mb]'
            if weather_location_yesterday is not None:
                for i in range(len(weather_location_yesterday.hourly)):
                    values_yesterday.append(weather_location_yesterday.hourly[i].pressure_mb)
                    if weather_location_day_before_yesterday is not None:
                        values_day_before_yesterday.append(weather_location_day_before_yesterday.hourly[i].pressure_mb)
            for weather_hour in self.weather_location_hourly:
                if re.match(datetime.today().strftime('%Y-%m-%d'), weather_hour.time):
                    values_today.append(weather_hour.pressure_mb)
        colors = []
        dates = []
        for i in range(forecast_days):
            dates.append((datetime.today() - timedelta(days=i)).strftime('%Y-%m-%d'))

        x = np.arange(len(hours_list))
        plt.figure(figsize=(16, 8))

        if weather_location_yesterday is not None:
            width = 0.2
            plt.bar(x - width, values_day_before_yesterday, width, label=dates[2])
            plt.bar(x, values_yesterday, width, label=dates[1])
            plt.bar(x + width, values_today, width, label=dates[0])
        elif weather_location_day_before_yesterday is not None:
            width = 0.3
            plt.bar(x - width / 2, values_yesterday, width, label=dates[1])
            plt.bar(x + width / 2, values_today, width, label=dates[0])
        else:
            width = 0.6
            plt.bar(x, values_today, width, label=dates[0])

        plt.legend()
        plt.xticks(ticks=x, labels=hours_list)

        plt.xlabel('Hour')
        plt.ylabel(data_type + measure)
        if data_type == 'Pressure':
            plt.ylim([975, 1050])
        elif data_type == 'Precipitation':
            plt.ylim(0)

        #for i in range(len(values_today)):
        #    plt.annotate(str(values_today[i]), xy=(hours_list[i], values_today[i]), ha='center', va='bottom')

        plt.savefig(filename)
        plt.close()

        self.source = ''
        self.source = filename
        self.reload()


class SpecificTabbedPanel(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False
        self.size_hint = 1, 1

        self.today = TabbedPanelItem(text='Today')
        self.forecast = TabbedPanelItem(text='Forecast')
        self.forecast_diff = TabbedPanelItem(text='Forecasts difference')
        self.chart_today = Chart()
        self.chart_forecast = Chart()
        self.chart_forecast_diff = Chart()

        self.add_widget(self.today)
        self.add_widget(self.forecast)
        self.add_widget(self.forecast_diff)

        self.today.add_widget(self.chart_today)
        self.forecast.add_widget(self.chart_forecast)
        self.forecast_diff.add_widget(self.chart_forecast_diff)

    # update charts
    def update(self, forecast_days, data_type):
        self.chart_today.weather_location_hourly = App.get_running_app().screen_manager.current_screen.weather_location.hourly
        self.chart_forecast.weather_location_hourly = App.get_running_app().screen_manager.current_screen.weather_location.hourly
        self.chart_forecast_diff.weather_location_hourly = App.get_running_app().screen_manager.current_screen.weather_location.hourly
        self.chart_today.set_today_chart(data_type)
        self.chart_forecast.set_forecast_chart(data_type, forecast_days)
        self.chart_forecast_diff.set_forecast_diff_chart(data_type, forecast_days)


# Screen with tabbed panels
class SpecificWeatherScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.tp_list = []

        self.weather_location = None
        self.night_hour = ''
        self.day_hour = ''
        self.forecast_days = 0
        self.database = None

    # Creating charts for specific city
    def create_self(self):
        self.ids.tp_temperature.tab_width = (self.parent.width-25) / 3
        self.ids.tp_wind.tab_width = (self.parent.width-25) / 3
        self.ids.tp_precipitation.tab_width = (self.parent.width-25) / 3
        self.ids.tp_humidity.tab_width = (self.parent.width-25) / 3
        self.ids.tp_cloudiness.tab_width = (self.parent.width-25) / 3
        self.ids.tp_pressure.tab_width = (self.parent.width-25) / 3
        # self.tp_list = [self.temperature_tp, self.wind_tp, self.precipitation_tp, self.humidity_tp,
        #                 self.cloudiness_tp, self.pressure_tp]

        """with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(SpecificTabbedPanel.update, self.tp_list)"""

        self.ids.tp_temperature.update(self.forecast_days, 'Temperature')
        self.ids.tp_wind.update(self.forecast_days, 'Wind')
        self.ids.tp_precipitation.update(self.forecast_days, 'Precipitation')
        self.ids.tp_humidity.update(self.forecast_days, 'Humidity')
        self.ids.tp_cloudiness.update(self.forecast_days, 'Cloudiness')
        self.ids.tp_pressure.update(self.forecast_days, 'Pressure')
