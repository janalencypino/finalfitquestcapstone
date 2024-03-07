# Import necessary modules from kivy library
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.clock import Clock
from kivy.metrics import dp


# Importing configuration and widget modules
import user.user_config as user_config
import admin.app_config as admin_config
from admin.admin_widgets import *
from user.user_widgets import *
from exercise_details import ExerciseDetails

# Countdown Screen class
class CountdownScreen(Screen):
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Singleton implementation to have only one instance of CountdownScreen
        if cls._instance is None:
            cls._instance = super(CountdownScreen, cls).__new__(cls, **kwargs)
        return cls._instance

    def __init__(self, sm: ScreenManager, app: App, **kwargs):
        super().__init__(**kwargs)
        self._sm = sm  # ScreenManager reference
        self._app = app  # App reference

        # ===============================
        #           Main layout
        # ===============================
        layout = FloatLayout(size_hint=[1.0, 1.0], pos_hint={'x': 0, 'y': 0})
        bg = Image(source=admin_config.app['background'], fit_mode="fill")
        layout.add_widget(bg)
        self._layout = layout

        # ===============================
        #           Label
        # ===============================
        label = Label(
            text="Are you ready? Your exercise starts in ",
            size_hint=[0.4, 0.3],
            pos_hint={'center_x': 0.5, 'y': 0.6},
            font_name=admin_config.font_name[3],
            font_size=admin_config.font_size[5],
        )
        layout.add_widget(label)
        self.add_widget(layout)

    def load_counter(self, initial_time: int = user_config.countdown_time):
        # Load and start the countdown timer
        layout = self._layout
        self.counter = Label(
            text=str(initial_time),
            size_hint=[0.4, 0.4],
            pos_hint={'center_x': 0.5, 'y': 0.25},
            font_name=admin_config.font_name[2],
            font_size=admin_config.font_size[6],
        )
        layout.add_widget(self.counter)

        def on_countdown_update(*args):
            try:
                value = int(self.counter.text)
            except BaseException as err:
                print(f"An error occurred. \n{err}")
                self._timer.cancel()

            value -= 1
            self.counter.text = str(value)
            if value < 1:
                # Change screen at this point.
                self._sm.transition = NoTransition()
                self._sm.current = 'exercise_start'

        self._timer = Clock.schedule_interval(
            on_countdown_update,
            1.0
        )

    def unload_counter(self):
        # Unload and stop the countdown timer
        while True:
            if not hasattr(self, 'counter'):
                continue

            self._layout.remove_widget(self.counter)
            del self.counter

            if not hasattr(self, '_timer'):
                continue

            self._timer.cancel()
            self._timer = None
            del self._timer
            break

    def on_pre_leave(self, *args):
        # Event handler called before leaving the screen
        self.unload_counter()

    def on_enter(self, *args):
        # Event handler called when entering the screen
        self.load_counter()