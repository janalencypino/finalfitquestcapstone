from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.properties import ListProperty
from functools import partial
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

import user.user_config as user_config
from user.user_widgets import *

import admin.app_config as admin_config
import admin.json_handler as json_handler

from admin.admin_widgets import *
from user_details import UserDetails
from exercise_details import ExerciseDetails
# from routine_details import RoutineDetails

from admin.admin_behavior import BackButtonDispatch
from user.user_selection import UserScreen
from user.user_exercise_start import ExerciseScreen


class SummaryScreen(Screen):
    _instance = None

    @property
    def progress_tracker(self):
        if not hasattr(self, '_progress_tracker'):
            self._progress_tracker = self._app.progress_track
        return self._progress_tracker

    @progress_tracker.setter
    def progress_tracker(self, value):
        return

    #

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SummaryScreen, cls).__new__(cls, **kwargs)
        return cls._instance

    def __init__(self, sm: ScreenManager, app: App,
                 exer_average: dict, exer_screen: ExerciseScreen,
                 user_screen: UserScreen, **kwargs):
        super().__init__(**kwargs)
        self._sm = sm
        self._app = app
        self.exer_average = exer_average
        self.exer_screen = exer_screen
        # Exfiltrate user from user_screen via user_screen.get_choice()
        self.user_screen = user_screen

        # ===============================
        #           Main layout
        # ===============================
        layout = FloatLayout(size_hint=[1.0, 1.0], pos_hint={'x': 0, 'y': 0})
        bg = Image(source=admin_config.app['background'], fit_mode="fill")
        layout.add_widget(bg)
        self._layout = layout

        self.add_widget(layout)

        logo = Image(
            source=admin_config.app['logo'],
            fit_mode="contain",
            size_hint=[0.35, 0.35],
            pos_hint={'center_x': 0.5, 'top': 0.95}
        )
        layout.add_widget(logo)

        # ===============================
        #       A simple toast
        # ===============================
        congratulations_label = Label(
            size_hint=[1, 0.40],
            pos_hint={'center_x': 0.5, 'top': 0.64},
            text=user_config.toast_message[1],
            font_name=admin_config.font_name[1],
            font_size=admin_config.font_size[6],
            valign='center',
            halign='center',
            line_height=0.4,
        )
        layout.add_widget(congratulations_label)
        congratulations_label.bind(
            size=congratulations_label.setter("text_size"))

        # congratulations_label
        # completed_label

        completed_label = Label(
            size_hint=[None, 0.40],
            width=1080,
            pos_hint={'center_x': 0.5, 'top': 0.55},
            text=user_config.toast_message[2],
            font_name=admin_config.font_name[3],
            font_size=admin_config.font_size[3],
            valign='center',
            halign='center',
            line_height=0.6,
        )
        layout.add_widget(completed_label)
        completed_label.bind(size=completed_label.setter('text_size'))

        back_btn = Button(
            text='BACK TO ROUTINE SELECTION',
            background_normal="",
            background_color=user_config.button_params['bg_color'],
            color=user_config.button_params['color'],
            font_name=admin_config.font_name[1],
            font_size=admin_config.font_size[3],
            size_hint=[0.44, 0.10],
            pos_hint={'x': 0.04, 'y': 0.05}
        )
        layout.add_widget(back_btn)
        BackButtonDispatch.on_release(back_btn, 'user_routine_selection', self._sm, 'right',
                                      self.update_results)

        progress_btn = Button(
            text="CHECK YOUR PROGRESS",
            background_normal="",
            background_color=user_config.button_params['bg_color'],
            color=user_config.button_params['color'],
            font_name=admin_config.font_name[1],
            font_size=admin_config.font_size[3],
            size_hint=[0.44, 0.10],
            pos_hint={'right': 0.96, 'y': 0.05}
        )
        layout.add_widget(progress_btn)
        BackButtonDispatch.on_release(
            progress_btn, 'progress_screen', self._sm, 'left')

    def update_results(self):
        if len(self.exer_average['exercises'] > 0):
            self.exer_screen.reset_average()

    def on_enter(self, *args):
        user: UserDetails = self.user_screen.get_choice()
        if user is None:
            raise RuntimeError(
                "No user specified! This screen should be unreachable!")

        # exer_list = self.exer_average['exercise']
        # avg_list = self.exer_average['average']
        # json_user = json_handler.JSONUser()

        exer_list = self.exer_average['exercise']
        avg_list = self.exer_average['average']
        json_user = json_handler.JSONUser()
        for i in range(len(exer_list)):
            exercise: ExerciseDetails = exer_list[i]
            avg_score: float = avg_list[i]
            user.add_exercise(exercise, avg_score)

        json_user.update()
        self.progress_tracker.on_add_list()
