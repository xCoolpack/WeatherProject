from kivy.uix.screenmanager import Screen


# Settings screen class
class SettingsScreen(Screen):
    night_hour = None
    day_hour = None

    # method changing night hour
    def change_night_hour(self, value):
        self.night_hour = value

    # method changing day hour
    def change_day_hour(self, value):
        self.day_hour = value