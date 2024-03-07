from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
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

from admin.admin_behavior import BackButtonDispatch
from user.user_selection import UserScreen
from user.user_exercise_start import ExerciseScreen
from user.user_exercise_cooldown import CooldownScreen


class BoundMethods:
    @staticmethod
    def on_instance_pos(instance, pos):
        if not hasattr(instance, 'rect'):
            return
        instance.rect.pos = pos

    @staticmethod
    def on_instance_size(instance, size):
        if not hasattr(instance, 'rect'):
            return
        instance.rect.size = size


class ProgressTrackScreen(Screen):
    _instance = None
    multiple_tiles_per_node = BooleanProperty(True)

    # method in the provided code implements a Singleton pattern by ensuring that only one instance of the ProgressTrackScreen class is created, 
    # and it returns the existing instance if it has already been instantiated
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ProgressTrackScreen, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self,
                 screen_manager: ScreenManager,
                 root_app: App,
                 exer_average: dict,
                 exer_screen: ExerciseScreen,
                 user_screen: UserScreen,
                 json_exer: json_handler.JSONExercise,
                 **kwargs):

        super().__init__(**kwargs)
        self._sm = screen_manager
        self._app = root_app
        self._index = 0
        self.exer_average = exer_average
        self.exer_screen = exer_screen
        self.user_screen = user_screen
        self.json_exer = json_exer

        # =============================
        #        Base Layout
        # =============================
        layout = FloatLayout(
            size_hint=[1.0, 1.0],
            pos_hint={'x': 0, 'y': 0}
        )
        self.add_widget(layout)
        self._layout = layout

        bg = Image(
            source=admin_config.app['background'],
            fit_mode="fill"
        )
        layout.add_widget(bg)

        logo = Image(
            source=admin_config.app['logo'],
            fit_mode="contain",
            size_hint=[None, None],
            size=[192, 192],
            pos_hint={'x': 0.04, 'top': 1}
        )
        layout.add_widget(logo)

        # =============================
        #       Progress Tracker
        #       Base Widget
        # =============================
        self.base_layout = FloatLayout(
            size_hint=[0.68, 0.92],
            pos_hint={'right': 0.96, 'top': 0.96}
        )
        layout.add_widget(self.base_layout)

        # =============================
        #           Top Area
        # =============================
        top_cabaret = FloatLayout(
            size_hint=[1.0, 0.25],
            pos_hint={'x': 0, 'top': 1.0},
        )
        self.base_layout.add_widget(top_cabaret)
        with top_cabaret.canvas:
            top_cabaret.color = Color(*user_config.button_params['purple'])
            top_cabaret.rect = RoundedRectangle(
                segments=50,
                radius=[(15, 15), (15, 15), (0, 0), (0, 0)],
                pos=top_cabaret.pos,
                size=top_cabaret.size,
            )
        top_cabaret.bind(pos=BoundMethods.on_instance_pos)
        top_cabaret.bind(size=BoundMethods.on_instance_size)

        cabaret_label = Label(
            size_hint=[1.0, 0.8],
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            text='PERFORMANCE RATINGS',
            font_name=admin_config.font_name[1],
            font_size=admin_config.font_size[2],
            halign='center',
            valign='center',
        )
        cabaret_label.bind(size=cabaret_label.setter('text_size'))
        top_cabaret.add_widget(cabaret_label)

        # =============================
        #         Bottom area
        # =============================
        content_area = FloatLayout(
            size_hint=[1.0, 0.75],
            pos_hint={'x': 0, 'y': 0},
        )
        self.base_layout.add_widget(content_area)
        with content_area.canvas:
            content_area.color = Color([0.75, 0.75, 0.75, 1])
            content_area.rect = RoundedRectangle(
                segments=50,
                radius=[(0, 0), (0, 0), (15, 15), (15, 15)],
                pos=content_area.pos,
                size=content_area.size,
            )
        content_area.bind(pos=BoundMethods.on_instance_pos)
        content_area.bind(size=BoundMethods.on_instance_size)

        grid_container = FloatLayout(
            size_hint=[0.9, 0.9],
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        content_area.add_widget(grid_container)

        scroll = ScrollView(
            size_hint=[1.0, None],
            pos_hint={'x': 0, 'y': 0}
        )
        grid_container.add_widget(scroll)
        grid_container.bind(height=scroll.setter('height'))

        grid = GridLayout(
            size_hint=[1.0, None],
            pos_hint={'x': 0, 'top': 1.0},
            cols=1,
            spacing=[0, 5],
        )
        scroll.add_widget(grid)
        grid.bind(minimum_height=grid.setter('height'))
        self.grid = grid

        # =============================
        #        Back button
        # =============================
        back_btn = Button(
            text='GO BACK',
            background_normal="",
            background_color=user_config.button_params['bg_color'],
            color=user_config.button_params['color'],
            font_name=admin_config.font_name[1],
            font_size=admin_config.font_size[3],
            size_hint=[0.20, 0.10],
            pos_hint={'x': 0.04, 'y': 0.05}
        )
        layout.add_widget(back_btn)
        BackButtonDispatch.on_release(
            back_btn, 'exercise_finished', self._sm, 'right')

    def create_routine_from_list(self,
                                 rout_name: str,
                                 avg_list: list[float],
                                 exer_list: list[ExerciseDetails]):

        # if score below 4 will not be displayed in progress tracking
        # for score in avg_list:
        #     if score >= .6:
        #         break
        # else:
        #     return

        base_widget = FloatLayout(
            size_hint=[1.0, None],
            height=300,
            pos_hint={'x': 0, 'y': 0}
        )
        self.grid.add_widget(base_widget)
        with base_widget.canvas:
            base_widget.color = Color(
                *user_config.button_params['light_color'])
            base_widget.rect = RoundedRectangle(
                segments=25,
                radius=[(10, 10), (10, 10), (10, 10), (10, 10)],
                pos=base_widget.pos,
                size=base_widget.size,
            )
        base_widget.bind(pos=BoundMethods.on_instance_pos)
        base_widget.bind(size=BoundMethods.on_instance_size)

        # =======================
        #   Add Label to exer_layout here
        # =======================
        rout_label = Label(
            size_hint=[0.2, 1.0],
            pos_hint={'x': 0, 'y': 0},
            font_name=admin_config.font_name[1],
            font_size=28,
            color=[1, 1, 1, 1],
            valign='center',
            halign='center'
        )
        base_widget.add_widget(rout_label)
        rout_label.bind(size=rout_label.setter('text_size'))

        if rout_name == "":
            self._index += 1
            rout_label.text = f'Custom Routine {self._index}'
        else:
            rout_label.text = rout_name

        with rout_label.canvas.before:
            rout_label.rect_color = Color(*user_config.button_params['color'])
            rout_label.rect = RoundedRectangle(
                segments=25,
                radius=[(15, 15), (0, 0), (0, 0), (15, 15)],
                pos=rout_label.pos,
                size=rout_label.size,
            )
        rout_label.bind(pos=BoundMethods.on_instance_pos)
        rout_label.bind(size=BoundMethods.on_instance_size)

        grid_container = FloatLayout(
            size_hint=[0.8, 0.8],
            pos_hint={'right': 1.0, 'center_y': 0.5}
        )
        base_widget.add_widget(grid_container)

        scroll = ScrollView(
            size_hint=[None, 1.0],
            pos_hint={'x': 0, 'y': 0},
            do_scroll_x=True,
        )
        grid_container.add_widget(scroll)
        grid_container.bind(width=scroll.setter('width'))

        grid = GridLayout(
            size_hint=[None, 1.0],
            pos_hint={'x': 0, 'y': 0},
            rows=1,
            col_default_width=350,
            col_force_default=True,
        )
        scroll.add_widget(grid)
        grid.bind(minimum_width=grid.setter('width'))

        # ==================================
        #         Add all exercises
        #           and scores
        # ==================================
        for i in range(len(exer_list)):
            exercise, score = exer_list[i], avg_list[i]
            # Coerce exercise into an ExerciseDetails object if need be.
            exercise = exercise if isinstance(
                exercise, ExerciseDetails) else self.json_exer.get_exercise(exercise)

            score = 1 if score > 1 else (0 if score < 0 else score)

            # if score below 4 will not be displayed in progress tracking
            # if score < .6:
            #     continue

            stars = CooldownScreen.star_rating(score)

            exer_layout = FloatLayout(
                size_hint=[None, 1.0],
                pos_hint={'x': 0, 'y': 0}
            )
            grid.add_widget(exer_layout)

            exer_image = Image(
                source=exercise.img_path,
                size_hint=[None, None],
                size=[128, 128],
                pos_hint={'center_x': 1.0, 'center_y': 0.7}
            )
            exer_layout.add_widget(exer_image)
            # exer_image.bind(height  = exer_image.setter('width'))
            
            if rout_name and exercise.name in self.exer_screen.customized_routine:
                user_sets = self.exer_screen.customized_routine[exercise.name].get('sets')
                user_reps = self.exer_screen.customized_routine[exercise.name].get('reps')
                sets_reps_text = f"Sets: {user_sets} Reps: {user_reps} - Customized"
            else:
                # Use default sets and reps for ready-made routine
                sets_reps_text = f"Sets: {exercise.sets} Reps: {exercise.reps}"

            exer_sets_reps = Label(
                text=sets_reps_text,
                size_hint=[0.75, 0.20],
                pos_hint={'center_x': 0.5, 'center_y': 0.15},
            )
            exer_layout.add_widget(exer_sets_reps)

            exer_grid = GridLayout(
                size_hint=[None, 0.2],
                pos_hint={'x': 0, 'y': 0},
                rows=1,
                spacing=[5, 0],
            )
            exer_layout.add_widget(exer_grid)
            exer_layout.bind(width=exer_grid.setter('width'))

            for i in range(1, 6):
                star_icon = Image(
                    source=app_config.path['icons']['star'],
                    size_hint=[None, None],
                    size=[40, 40],
                    pos_hint={'center_x': 0.5, 'center_y': 0.5}
                )
                exer_grid.add_widget(star_icon)
                star_icon.bind(height=star_icon.setter('width'))

                if i <= stars:
                    star_icon.color = [1, 1, 1, 1]
                else:
                    star_icon.color = [0.2, 0.2, 0.2, 1]

    def add_routine_from_list(self,
                              avg_list: list[float],
                              exer_list: list[ExerciseDetails]):

        user: UserDetails = self.user_screen.get_choice()
        if user is None:
            raise RuntimeError(
                "\nNo user was selected!")

        rout_name = self.exer_screen.routine_name
        if rout_name != '':
            user.add_routine_info(rout_name, avg_list, exer_list)
        else:
            user.add_routine_info("", avg_list, exer_list)

        self._index = 0
        self.grid.clear_widgets()
        for routine_dict in user.routines:
            self.create_routine_from_list(
                routine_dict['name'], routine_dict['average'], routine_dict['exercise'])

    def add_average_list(self,
                         avg_list: list[float],
                         exer_list: list[ExerciseDetails]):
        exer_map = {}
        out_exer_list = []
        out_avg_list = []

        avg_score = 0.0
        avg_size = 0
        for i in range(len(avg_list)):
            exercise = exer_list[i]
            avg_score += avg_list[i]
            avg_size += 1
            if ((self.multiple_tiles_per_node) or
                    (not exercise in exer_map)):
                exer_map[exercise] = True

                out_exer_list.append(exercise)
                out_avg_list.append(avg_score / avg_size)
                avg_score = 0.0
                avg_size = 0

        if len(out_exer_list) < 1:
            return

        self.add_routine_from_list(out_avg_list, out_exer_list)
        # self.grid.clear_widgets()
        # for

    # def on_pre_enter(self):
    #     self.add_average_list(
    #         self.exer_average['average'],
    #         self.exer_average['exercise']
    #     )
    #     self.exer_screen.reset_average()

    def on_add_list(self):
        self.add_average_list(
            self.exer_average['average'],
            self.exer_average['exercise']
        )
        self.exer_screen.reset_average()

    def on_pre_enter(self):
        self.on_add_list()
