# Class contains weather data in specific hour
class WeatherHourly:
    def __init__(self, time, text, icon, temp, wind_kph, wind_dir, precip, press, hum, cloud):
        self.time = time
        self.text = text
        self.icon = icon
        self.temperature = temp
        self.wind_velocity = wind_kph
        self.wind_direction = wind_dir
        self.precipitation = precip
        self.pressure_mb = press
        self.humidity = hum
        self.cloudiness = cloud

    def get_temperature_str(self):
        return f'{self.temperature} \xb0C'

    def get_tuple(self, id):
        return (self.time,
                self.temperature,
                self.wind_velocity,
                self.wind_direction,
                self.precipitation,
                self.pressure_mb,
                self.humidity,
                self.cloudiness,
                id)

    @classmethod
    def create_from_json(cls, date, current_data):
        return cls(date,
                   current_data.get('condition').get('text'),
                   'http:'+str(current_data.get('condition').get('icon')),
                   current_data.get('temp_c'),
                   current_data.get('wind_kph'),
                   current_data.get('wind_dir'),
                   current_data.get('precip_mm'),
                   current_data.get('pressure_mb'),
                   current_data.get('humidity'),
                   current_data.get('cloud'))

    @classmethod
    def create_from_database(cls, data_tuple):
        _, time, temperature, wind_velocity, wind_direction, precip, pressure, humidity, cloudiness, _ = data_tuple
        return cls(time,
                   None,
                   None,
                   temperature,
                   wind_velocity,
                   wind_direction,
                   precip,
                   pressure,
                   humidity,
                   cloudiness)

    def __str__(self):
        return f'Time: {self.time}\n' \
               f'Temperature: {self.temperature} \xb0C\n' \
               f'Wind velocity: {self.wind_velocity} km/h\n' \
               f'Wind direction: {self.wind_direction}\n' \
               f'Precipitation: {self.precipitation} mm\n' \
               f'Pressure: {self.pressure_mb} Mb\n' \
               f'Humidity: {self.humidity}%\n' \
               f'Cloudiness: {self.cloudiness}%\n'

    def __repr__(self):
        return f'Time: {self.time}\n' \
               f'Temperature: {self.temperature} \xb0C\n' \
               f'Wind velocity: {self.wind_velocity} km/h\n' \
               f'Wind direction: {self.wind_direction}\n' \
               f'Precipitation: {self.precipitation} mm\n' \
               f'Pressure: {self.pressure_mb} Mb\n' \
               f'Humidity: {self.humidity}%\n' \
               f'Cloudiness: {self.cloudiness}%\n'
