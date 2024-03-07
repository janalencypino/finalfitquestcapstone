# =================================
#       Import Kivy Widgets
# =================================
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.animation import Animation
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.metrics import dp
import json

from kivy.clock import Clock

# =================================
#       Import local files
# =================================
import admin.app_config as app_config
import user.user_config as user_config

from admin.json_handler import JSONExercise, JSONRoutine, ExerciseDetails, RoutineDetails
from admin.admin_widgets import *

class ExerciseTabs:
    @staticmethod
    def add_exercise_tab(admin: Screen, tab_panel: TabbedPanel):
        if (not isinstance(admin, AdminDashboard)):
            return None
        tab                 = TabbedPanelItem(text='Add Exercises', font_size=app_config.tab['font_size'])
        
        tab_container       = FloatLayout(
            size_hint       = [1.0, 1.0],
            pos_hint        = {'x': 0.0,'y': 0.0}
        )
        tab.add_widget(tab_container)
        tab_content         = BoxLayout(
            orientation     = 'vertical',
            size_hint       = [1.0, 1.0],
            pos_hint        = {'x': 0, 'y': 0},
        )
        tab_container.add_widget(tab_content)

        # Image Upload Button
        #TO-DO: replace source image path with a sensible path.  
        admin.upload_image_btn  = upload_image_btn  = ImageButton(
            source              = app_config.path['icons']['exercise'],
            size_hint           = [None, 0.14],
            width               = 100,
            pos_hint            = {'right': 0.95, 'y': 0.05},
            fit_mode            = 'fill'
        )
        upload_image_btn.bind(height        = upload_image_btn.setter('width'))
        with upload_image_btn.canvas.before:
            upload_image_btn.rect_color     = Color(*user_config.button_params['light_color'])
            upload_image_btn.rect           = Rectangle(
                pos                         = upload_image_btn.pos,
                size                        = upload_image_btn.size,
            )
        upload_image_btn.bind(pos           = admin.on_button_pos)
        upload_image_btn.bind(size          = admin.on_button_size)
        upload_image_btn.bind(on_release    = admin.open_file_chooser)
        tab_container.add_widget(upload_image_btn)

        def show_success_popup():
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text="Exercise added successfully!"))

            popup = Popup(title="Success", content=content, size_hint=(None, None), size=(400, 200))
            popup.open()

        def on_exercise_defined(instance):
            if ((not admin._name.text) or
                (int(admin._reps.text) <= 0) or 
                (int(admin._sets.text) <= 0) or 
                (int(admin._dur.text) <= 0)):
                # Create an error label
                error_label = Label(text="Please fill in all fields.", color=(1, 0, 0, 1))

                # Check if the error layout already exists, if not, create it
                if not hasattr(admin, '_error_layout'):
                    error_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=50)
                    admin._error_layout = error_layout
                    tab_content.add_widget(error_layout)

                # Create an empty BoxLayout for spacing
                spacing_layout = BoxLayout(size_hint_y=None, height=-100)

                # Clear any previous content in the error layout
                admin._error_layout.clear_widgets()

                # Add the spacing layout and error label to the error layout
                admin._error_layout.add_widget(spacing_layout)
                admin._error_layout.add_widget(error_label)

                # Schedule a function to remove the error layout and error label after a delay
                def remove_error_layout(dt):
                    if hasattr(admin, '_error_layout'):
                        tab_content.remove_widget(admin._error_layout)
                        delattr(admin, '_error_layout')
                Clock.schedule_once(remove_error_layout, 3)  # Adjust the delay as needed (3 seconds in this example)
                return

            admin.exer_list.add_exercise(
                admin._name.text,
                int(admin._reps.text),
                int(admin._sets.text),
                int(admin._dur.text),
                admin._desc.text,
                img_path    = admin._image_src
            )
            Clock.schedule_once(
                admin.on_add_exer_text_clear,
                0.0,
            )
            admin.draw_exercise_widgets()

            # Show the success pop-up
            show_success_popup()

        add_exercise_btn    = Button(text='Add New Exercise', size_hint_y=None, height=50)
        add_exercise_btn.bind(on_release=on_exercise_defined)
        tab_content.add_widget(add_exercise_btn)
        
        
        upload_label        = Label(
            text            = 'Upload Image:',
            size_hint       = [0.35, 0.15],
            pos_hint        = {'right': 0.85, 'y': 0.05},
            font_size       = app_config.font_size[0],
            font_name       = app_config.font_name[0],
            halign          = 'right',
            valign          = 'center'
        )
        upload_label.bind(size  = upload_label.setter('text_size'))
        tab_container.add_widget(upload_label)
        # Table (using GridLayout)
        table               = GridLayout(cols=2, row_force_default=True, row_default_height=60, spacing=[0,5])
        admin._table        = table
        admin.draw_table()
        tab_content.add_widget(table)

        return tab

    @staticmethod
    def manage_exercise_tab(admin: Screen, tab_panel: TabbedPanel):
        if (not isinstance(admin, AdminDashboard)):
            return None
        tab                         = TabbedPanelItem(text='Manage Exercises', font_size=app_config.tab['font_size'])
        base_layout                 = FloatLayout(
            size_hint               = [1.0, 1.0],
        )
        tab.add_widget(base_layout)

        bg_layout                   = BGFloatLayout(
            size_hint               = [0.72, 0.84],
            pos_hint                = {'center_x': 0.5, 'center_y': 0.5}            
        )
        base_layout.add_widget(bg_layout)

        bg_layout.border_size       = 5
        bg_layout.bg_color.rgba     = [0.16, 0.16, 0.16, 1]
        bg_layout.border_color.rgba = [0.35, 0.35, 0.35, 1]

        # =================================
        #       Create exercise manager
        # =================================

        manager_layout              = FloatLayout(
            size_hint               = [0.88, 0.88],
            pos_hint                = {'center_x' : 0.5, 'center_y': 0.5}
        )
        bg_layout.add_widget(manager_layout)

        # =================================
        #           Left Layout
        # =================================
        scroll_layout               = FloatLayout(
            size_hint               = [0.28, 1.0],
            pos_hint                = {'x' : 0, 'y': 0}
        )
        manager_layout.add_widget(scroll_layout)

        scroll                      = ScrollView(
            size_hint_x             = 1.0,
            size_hint_y             = None,
            do_scroll_y             = True,
            pos_hint                = {'center_x' : 0.5, 'center_y': 0.5}
        )
        scroll_layout.add_widget(scroll)

        box                         = GridLayout(
            cols                    = 1,
            size_hint               = [1.0, None],
            pos_hint                = {'x': 0, 'y': 0},
            row_default_height      = app_config.admin_page['exercise_manager']['selection_height'],
            row_force_default       = True,
        )
        admin._exercise_box         = box
        scroll.add_widget(box)

        scroll_layout.bind(height   = scroll.setter('height'))
        box.bind(minimum_height     = box.setter("height"))

        # =================================
        #           Right Layout
        # =================================
        panel_layout                = FloatLayout(
            size_hint               = app_config.admin_page['exercise_manager']['panel_layout_size'],
            pos_hint                = {'x': 0.32, 'y': 0}
        )
        manager_layout.add_widget(panel_layout)

        admin._exer_fields          = {}
        admin._exer_panel           = panel_layout
        admin._cur_exercise         = None

        # =================================
        #    Store Reps, Sets and Duration
        #    fields inside a GridLayout
        # =================================
        panel_grid                  = GridLayout(
            size_hint               = [1.0, 0.32],
            pos_hint                = {'x': 0, 'y': 0.68},
            cols                    = 2,
        )
        panel_layout.add_widget(panel_grid)

        # Add reps field.
        panel_grid.add_widget(LeftLabel(text    = 'Repetitions:'))
        admin._exer_fields['reps']              = IntInput()
        panel_grid.add_widget(admin._exer_fields['reps'])

        # Add sets field.
        panel_grid.add_widget(LeftLabel(text    = 'Sets:'))
        admin._exer_fields['sets']              = IntInput()
        panel_grid.add_widget(admin._exer_fields['sets'])

        # Add duration field.
        panel_grid.add_widget(LeftLabel(text    = 'Duration:'))
        admin._exer_fields['duration']          = IntInput()
        panel_grid.add_widget(admin._exer_fields['duration'])

        # Add description field.
        panel_desc_grid             = GridLayout(
            size_hint               = [1.0, 0.64],
            pos_hint                = {'x': 0, 'y': 0},
            cols                    = 1
        )
        panel_layout.add_widget(panel_desc_grid)

        desc_label                  = LeftLabel(
            text            = 'Description:',
            height          = 50,
        )
        desc_label.bind(size        = desc_label.setter('text_size'))

        panel_desc_grid.add_widget(desc_label)
        admin._exer_fields['description']       = TextInput()
        panel_desc_grid.add_widget(admin._exer_fields['description'])

        # =================================
        #       Exercise box done
        # =================================
        def on_entry_save(instance):
            exercise                = admin._cur_exercise
            if exercise is None:
                return
            
            exer_fields             = admin._exer_fields
            # Check if all fields are filled
            if not all(exer_fields[field].text for field in ['reps', 'sets', 'duration', 'description']):
                error_popup = Popup(title='Error', content=Label(text='Please fill in all fields'), size_hint=(None, None), size=(400, 200))
                error_popup.open()
                return
            exercise.reps           = int(exer_fields['reps'].text)
            exercise.sets           = int(exer_fields['sets'].text)
            exercise.duration       = int(exer_fields['duration'].text)
            exercise.description    = exer_fields['description'].text

            admin.exer_list.update()

            success_popup = Popup(title='Success', content=Label(text='Exercise saved successfully'), size_hint=(None, None), size=(400, 200))
            success_popup.open()

        save_btn = Button(text="Save", size_hint=[None, None], size=(100, 50), pos_hint={'right': 1, 'y': 0})
        save_btn.bind(on_press=on_entry_save)
        base_layout.add_widget(save_btn)

        admin.draw_exercise_widgets()
        # =================================
        #       Floating Delete Button
        # =================================
        del_button                  = ImageButton2(
            size_hint               = [None, None],
            size                    = [40, 40],
            pos_hint                = {'right': 1.0, 'y': 0.50},
            source                  = app_config.path['icons']['delete'],
        )
        panel_layout.add_widget(del_button)
        def on_bind_del_button(del_button: ImageButton2):
            def on_del_request(instance):
                nonlocal admin
                admin.app_data['cur_exercise'] = admin._cur_exercise.name
                admin.popup.open()
            del_button.bind(on_release=on_del_request)
            
        on_bind_del_button(del_button)
        return tab
    
class RoutineTabs:
    @staticmethod
    def add_routine_tab(admin: Screen, tab_panel: TabbedPanel):
        if (not isinstance(admin, AdminDashboard)):
            return None
        
        admin._routine_elements     = {}
        admin._exercises            = []
        tab                         = TabbedPanelItem(text='Add Routine', font_size=app_config.tab['font_size'])

        base_layout                 = FloatLayout(
            size_hint               = [1.0, 1.0],
        )
        tab.add_widget(base_layout)

        def create_add_routine_tab_left(admin, base_layout):
            # Create left side area
            left_layout                 = FloatLayout(
                size_hint               = [0.60, 0.90],
                pos_hint                = {'x': 0.05, 'y': 0.05},
            )
            base_layout.add_widget(left_layout)

            # Routine text layout:
            rout_name_layout            = GridLayout(
                rows                    = 1,
                cols                    = 2,
                size_hint               = [1.0, 0.08],
                pos_hint                = {'x': 0, 'y': 0.92},
            )
            left_layout.add_widget(rout_name_layout)

            # Routine text section:
            rout_name_label             = Label(
                text                    = 'Routine Name:',
                font_name               = app_config.font_name[0],
                font_size               = app_config.font_size[0],
                size_hint               = [0.36, 1.0],
                pos_hint                = {'x': 0, 'y': 0},
                valign                  = 'top',
            )
            rout_name_layout.add_widget(rout_name_label)

            rout_name_text                      = TextInput(
                font_name                       = app_config.font_name[0],
                font_size                       = app_config.font_size[0],
                size_hint                       = [0.64, 1.0],
                pos_hint                        = {'x': 0, 'y': 0}
            )
            rout_name_layout.add_widget(rout_name_text)
            admin._routine_elements['name']     = rout_name_text

            # Routine text description layout:
            rout_desc_layout            = GridLayout(
                rows                    = 2,
                cols                    = 1,
                size_hint               = [0.48, 0.72],
                pos_hint                = {'x': 0, 'y': 0.12},
                spacing                 = [0, 16],
            )
            left_layout.add_widget(rout_desc_layout)

            # Routine text description section:
            rout_desc_label             = Label(
                text                    = 'Routine Description:',
                font_name               = app_config.font_name[0],
                size_hint               = [1.0, 0.08],
                pos_hint                = {'x': 0, 'y': 0},
                valign                  = 'center',
                halign                  = 'left'
            )
            rout_desc_layout.add_widget(rout_desc_label)

            rout_desc_text              = TextInput(
                font_name               = app_config.font_name[0],
                font_size               = app_config.font_size[0],
                size_hint               = [1.0, 0.92],
                pos_hint                = {'x': 0, 'y': 0}
            )
            rout_desc_layout.add_widget(rout_desc_text)
            admin._routine_elements['description']   = rout_desc_text

            # Make sure rout_desc_label is positioned to the left.
            rout_name_label.bind(size=rout_name_label.setter('text_size'))
            rout_desc_label.bind(size=rout_desc_label.setter('text_size'))
        
            # =============================
            #       Add Exercise Panel 
            # =============================
            exer_panel_layout                   = BGFloatLayout(
                size_hint                       = [0.40, 0.72],
                pos_hint                        = {'right': 1.0, 'y': 0.12}
            )
            exer_panel_layout.bg_color.rgba     = [0.15, 0.15, 0.15, 1]
            exer_panel_layout.border_color.rgba = [0, 0, 0, 1]
            exer_panel_layout.border_size       = 1.5
            left_layout.add_widget(exer_panel_layout)

            exer_title                          = Label(
                text                            = "Exercise:",
                size_hint                       = [0.8, 0.16],
                pos_hint                        = {'center_x': 0.5, 'y': 0.84},
                halign                          = 'left',
                valign                          = 'center'
            )
            exer_panel_layout.add_widget(exer_title)
            exer_title.bind(size = exer_title.setter("text_size"))

            # ===============================
            #       Drop-down Button
            # ===============================
            exer_dropdown                       = DropdownOption(
                title                           = "-- Exercise --",
                size_hint                       = [0.8, 0.60],
                pos_hint                        = {'center_x': 0.5, 'y': 0.24},
                button_hint_y                   = 0.20,
                option_height                   = 35,
                option_space                    = 0
            )
            exer_panel_layout.add_widget(exer_dropdown)
            admin._routine_elements['exercise'] = exer_dropdown

            exercise_list: JSONExercise         = admin.exer_list
            for exercise in exercise_list.extract_list():
                exer_dropdown.add_option(exercise.name)

            # ===============================
            #       Field grid for parametrization
            # ===============================
            field_grid                          = GridLayout(
                cols                            = 2,
                size_hint                       = [0.8, 0.28],
                pos_hint                        = {'center_x': 0.5, 'y': 0.36},
            )
            exer_panel_layout.add_widget(field_grid, 1)

            field_reps_label                    = LeftLabel(
                text                            = 'Reps',
                pos_hint                        = {'x': 0.1, 'y': 0},
            )
            field_grid.add_widget(field_reps_label)
            field_reps_input                    = IntInput()
            field_grid.add_widget(field_reps_input)

            field_sets_label                    = LeftLabel(
                text                            = 'Sets',
                pos_hint                        = {'x': 0.1, 'y': 0},
            )
            field_grid.add_widget(field_sets_label)
            field_sets_input                    = IntInput()
            field_grid.add_widget(field_sets_input)

            admin._routine_elements['reps']     = field_reps_input
            admin._routine_elements['sets']     = field_sets_input
            field_reps_input.disabled           = field_sets_input.disabled = True

            # =======================================
            #       Change on_selection_made
            # =======================================
            def on_selection_made(exer_dropdown, instance):
                field_reps_input.disabled       = field_sets_input.disabled = instance is None
                if instance is None:
                    field_reps_input.text       = field_sets_input.text = ""

            exer_dropdown.on_selection_made     = on_selection_made

            # =======================================
            #       Create a submit button
            # =======================================
            submit_btn                          = Button(
                text                            = 'Submit',
                pos_hint                        = {'right': 0.96, 'y': 0.04},
                size_hint                       = [0.40, 0.12],
                disabled                        = True
            )
            exer_panel_layout.add_widget(submit_btn, 1)
            admin._routine_elements['submit']   = submit_btn

            # =======================================
            #       Handle submit button logic
            # =======================================
            def on_submit(instance):
                nonlocal admin
                rout_elements = admin._routine_elements
                exer_name = rout_elements['exercise'].get_option()
                reps = int(rout_elements['reps'].text)
                sets = int(rout_elements['sets'].text)
                grid = rout_elements['grid']

                rout_elements['exercise'].clear_option()
                admin.add_rout_check_submit()
                
                # Add exercise
                base_exercise = admin.exer_list.get_exercise(exer_name)
                exercise = base_exercise.copy()
                exercise.reps = reps
                exercise.sets = sets
                exercise.duration = base_exercise.duration * exercise.reps / base_exercise.reps

                admin._exercises.append(exercise)

                # Add an unselectable widget.
                exer_container = BGFloatLayout(
                    size_hint=[0.9, None],
                    pos_hint={'center_x': 0.5, 'y': 0}
                )
                exer_container.bg_color.rgba = [0.8, 0.8, 0.8, 1]
                grid.add_widget(exer_container)

                # Add a grid showing all contents
                inner_grid = GridLayout(
                    cols=3,  # Added one more column for the delete button
                    rows=3,
                    size_hint=[0.9, 0.9],
                    pos_hint={'center_x': 0.5, 'center_y': 0.5}
                )
                exer_container.add_widget(inner_grid)

                # Finally, the exercise content/s
                inner_grid.add_widget(Label(
                    color=[0, 0, 0, 1],
                    text="Exercise:"
                ))
                inner_grid.add_widget(Label(
                    color=[0, 0, 0, 1],
                    text=exercise.name,
                ))
                inner_grid.add_widget(Label(
                    color=[0, 0, 0, 1],
                    text="Reps:"
                ))
                inner_grid.add_widget(Label(
                    color=[0, 0, 0, 1],
                    text=str(reps),
                ))
                inner_grid.add_widget(Label(
                    color=[0, 0, 0, 1],
                    text="Sets:"
                ))
                inner_grid.add_widget(Label(
                    color=[0, 0, 0, 1],
                    text=str(sets),
                ))

                # Add delete button
                delete_button = Button(
                    text="Delete",
                    size_hint=(0.2, 1),
                    pos_hint={'center_x': 0.5, 'center_y': 0.5},
                    on_release=lambda btn: grid.remove_widget(exer_container) or admin._exercises.remove(exercise)
                )
                inner_grid.add_widget(delete_button)

            submit_btn.bind(on_release=on_submit)

        def create_add_routine_tab_right(admin, base_layout):
            right_layout                        = BGFloatLayout(
                size_hint                       = [0.27, 0.79],
                pos_hint                        = {'right': 0.95, 'top': 0.95}
            )
            right_layout.bg_color.rgba          = [0.2, 0.2, 0.2, 1]
            right_layout.border_color.rgba      = [0, 0, 0, 1]
            right_layout.border_size            = 2
            base_layout.add_widget(right_layout)

            exer_label                          = Label(
                text                        = "Registered Exercises:",
                size_hint                   = [1.0, 0.15],
                pos_hint                    = {'x': 0, 'top': 0.95}
            )
            right_layout.add_widget(exer_label)

            reg_background                      = BGFloatLayout(
                size_hint                   = [1.0, 0.8],
                pos_hint                    = {'x': 0, 'y': 0},
            )
            reg_background.bg_color.rgba        = [0.4, 0.4, 0.4, 1]
            right_layout.add_widget(reg_background)

            reg_scroll_container                = FloatLayout(
                size_hint                       = [0.90, 0.90],
                pos_hint                        = {'center_x': 0.5, 'center_y': 0.5},
            )
            reg_background.add_widget(reg_scroll_container)

            reg_scroll                          = ScrollView(
                size_hint                       = [1.0, None],
                pos_hint                        = {'x': 0, 'y': 0},
                do_scroll_y                     = True
            )
            reg_scroll_container.add_widget(reg_scroll)
            reg_scroll_container.bind(height    = reg_scroll.setter('height'))

            reg_grid                            = GridLayout(
                cols                            = 1,
                size_hint                       = [1.0, None],
                pos_hint                        = {'x': 0, 'y': 0},
                spacing                         = 10,
            )
            reg_scroll.add_widget(reg_grid)
            reg_grid.bind(minimum_height        = reg_grid.setter('height'))
            admin._routine_elements['grid']     = reg_grid

        create_add_routine_tab_left(admin, base_layout)
        create_add_routine_tab_right(admin, base_layout)

        # =========================================
        #       Handle send button
        # =========================================
        send_btn            = Button(
            text            = "Add New Routine",
            pos_hint        = {'right': 0.95, 'y': 0.04},
            size_hint       = [0.15, 0.08]
        )
        base_layout.add_widget(send_btn)
        admin._routine_elements['send'] = send_btn
        admin.add_rout_check_send()

        def on_send_routine(send_btn):
            nonlocal admin
            rout_elements   = admin._routine_elements
            admin.rout_list.add_routine(
                rout_elements['name'].text,
                rout_elements['description'].text,
                admin._exercises,
            )
            
            # Clear widgets and data
            rout_elements['exercise'].clear_option()
            rout_elements['name'].text = rout_elements['description'].text = ""
            rout_elements['grid'].clear_widgets()
            admin._exercises            = []

             # Display success popup
            success_popup = Popup(title='Success', content=Label(text='Routine submitted successfully'), size_hint=(None, None), size=(400, 200))
            success_popup.open()

            admin.add_rout_check()

        send_btn.bind(on_release    = on_send_routine)

        # =========================================
        #       Handle current_tab focus and
        #       unfocus
        # =========================================
        last_tab    = None
        def on_tab_update(tab_panel, value):
            nonlocal last_tab, tab, admin
            
            rout_elements   = admin._routine_elements
            if (value == tab) and (last_tab != tab):
                rout_elements['start']  = Clock.schedule_interval(
                    admin.add_rout_check,
                    0.0
                )
            elif (value != tab) and (last_tab == tab):
                rout_elements['start'].cancel()
                del rout_elements['start']

            last_tab        = value
            
        tab_panel.bind(current_tab = on_tab_update)
        return tab

    @staticmethod
    def manage_routine_tab(admin: Screen, tab_panel: TabbedPanel):
        if (not isinstance(admin, AdminDashboard)):
            return None
        tab                         = TabbedPanelItem(
            text                    = 'Manage Routines',
            font_size               = app_config.tab['font_size']
        )
        admin._tab                  = tab
        admin._manage_rout_elem     = {
            'no_elem_base'          : None,
            'elem_base'             : None,
        }
        admin._manage_params        = {
            'routine'               : None,
            'prev_routine'          : None,
            'exercise'              : None,
            'prev_exercise'         : None,
        }


        root_layout                 = FloatLayout(
            size_hint               = [1.0, 1.0],
            pos_hint                = {'x': 0, 'y': 0}
        )
        tab.add_widget(root_layout)

        #   ================================
        #       Display when no routines
        #       have been created
        #   ================================
        no_elem_base_layout         = FloatLayout(
            size_hint               = [1.0, 1.0],
            pos_hint                = {'x': 0, 'y': 0}
        )
        root_layout.add_widget(no_elem_base_layout)
        admin._manage_rout_elem['no_elem_base'] = no_elem_base_layout

        tab_content                 = Label(
            text                    = 'Here, you can manage ready made routines.',
            size_hint               = [1.0, 1.0],
            pos_hint                = {'x': 0, 'y': 0}
        )
        no_elem_base_layout.add_widget(tab_content)

        #   ================================
        #           Actual content
        #   ================================
        base_layout                 = FloatLayout(
            size_hint               = [1.0, 1.0],
            pos_hint                = {'x': 0, 'y': 0}
        )
        root_layout.add_widget(base_layout)
        admin._manage_rout_elem['elem_base']    = base_layout

        
        def delete_selected_routine(confirm_popup):
            routines_grid = admin._manage_rout_elem['grid']
            selected_routine = admin._manage_params['routine']

            # Remove the routine from the UI
            for child in list(routines_grid.children):
                if child.text == selected_routine.text:  # Assuming the text represents the routine name
                    routines_grid.remove_widget(child)
                    break

            # Remove the routine from the JSON file
            if selected_routine is not None:
                with open('routines.json', 'r+') as file:
                    routines_data = json.load(file)
                    routines_data = [routine for routine in routines_data if routine['routine_name'] != selected_routine.text]
                    file.seek(0)  # Reset the file pointer to the beginning
                    json.dump(routines_data, file, indent=4)
                    file.truncate()  # Remove any remaining content after the updated data

            # Additionally, perform other actions related to routine deletion here
            admin._manage_params['routine'] = None  # Reset the selected routine

            confirm_popup.dismiss()  # Close the confirmation popup

            # Creating success popup
            success_popup = Popup(title='Success',
                                content=Label(text='Routine successfully deleted.'),
                                size_hint=(None, None), size=(400, 300))
            success_popup.open()


        def delete_routine():
            selected_routine = admin._manage_params['routine']
            if selected_routine is not None:
                confirm_popup = Popup(title='Confirm Deletion',
                                      size_hint=(None, None), size=(400, 300))

                content_layout = GridLayout(cols=1, spacing=10)
                confirm_message = Label(text='Are you sure you want to delete this routine?')

                button_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=50)
                yes_button = Button(text='Yes', size_hint_x=None, width=100)
                no_button = Button(text='No', size_hint_x=None, width=100)

                yes_button.bind(on_press=lambda instance: delete_selected_routine(confirm_popup))
                no_button.bind(on_press=confirm_popup.dismiss)

                button_layout.add_widget(yes_button)
                button_layout.add_widget(no_button)

                content_layout.add_widget(confirm_message)
                content_layout.add_widget(button_layout)

                confirm_popup.content = content_layout
                confirm_popup.open()


        #   ====================================
        #             Left Layout
        #   ====================================
        left_layout                             = BGFloatLayout(
            size_hint                           = [0.35, 0.9],
            pos_hint                            = {'x': 0.05, 'center_y': 0.5}
        )
        left_layout.bg_color.rgba               = [0.2, 0.2, 0.2, 1.0]
        left_layout.border_color.rgba           = [0, 0, 0, 1]
        left_layout.border_size                 = 2
        base_layout.add_widget(left_layout)

        right_layout                            = FloatLayout(
            size_hint                           = [0.5, 0.9],
            pos_hint                            = {'right': 0.95, 'center_y': 0.5}
        )
        base_layout.add_widget(right_layout)
        admin._manage_rout_elem['right_layout'] = right_layout

        def left_layout_elements(admin, left_layout):
            exer_bg                                 = BGFloatLayout(
                size_hint                           = [1.0, 0.25],
                pos_hint                            = {'center_x': 0.5, 'top': 1}
            )
            exer_bg.bg_color.rgba                   = [0.25, 0.25, 0.25, 1]
            left_layout.add_widget(exer_bg)

            rout_label                              = Label(
                text                                = 'Routine:',
                size_hint                           = [1, 1],
                font_size                           = 32,
                pos_hint                            = {'center_x': 0.5, 'y': 0}
            )
            exer_bg.add_widget(rout_label)

            selection_bg                            = BGFloatLayout(
                size_hint                           = [1.0, 0.75],
                pos_hint                            = {'x': 0, 'y': 0}
            )
            selection_bg.bg_color.rgba              = [0.5, 0.5, 0.5, 1]
            left_layout.add_widget(selection_bg)

            selection_scroll                        = ScrollView(
                size_hint                           = [1.0, None],
                do_scroll_y                         = True,
                pos_hint                            = {'x': 0, 'y': 0}
            )
            selection_bg.add_widget(selection_scroll)
            selection_bg.bind(height = selection_scroll.setter('height'))

            select_grid                             = GridLayout(
                cols                                = 1,
                size_hint                           = [1.0, None],
                pos_hint                            = {'x': 0, 'y': 0}
            )
            selection_scroll.add_widget(select_grid)
            select_grid.bind(minimum_height         = select_grid.setter('height'))
            admin._manage_rout_elem['grid']         = select_grid

            # Delete button
            del_routine_button = ImageButton2(
                size_hint=[None, None],
                size=[50, 50],  # Increase the size of the button
                pos_hint={'x': 0.45, 'center_y': 0.35},  # Move the button to the left
                source=app_config.path['icons']['delete'],
            )
            del_routine_button.bind(on_press=lambda instance: delete_routine())
            left_layout.add_widget(del_routine_button)

        def right_layout_elements(admin, right_layout):
            routine_grid    = GridLayout(
                cols        = 2,
                rows        = 2,
                size_hint   = [0.90, 0.40],
                pos_hint    = {'center_x': 0.5, 'top': 0.95}
            )
            right_layout.add_widget(routine_grid)

            _label          = LeftLabel(
                size_hint   = [0.30, 0.30],
                pos_hint    = {'x': 0, 'y': 0},
                text        = 'Routine Name:'
            )
            routine_grid.add_widget(_label)

            name_field      = TextInput(
                size_hint   = [0.70, 0.30],
                pos_hint    = {'x': 0, 'y': 0},
            )
            routine_grid.add_widget(name_field)
            admin._manage_rout_elem['name'] = name_field

            _label          = LeftLabel(
                size_hint   = [0.30, 0.70],
                pos_hint    = {'x': 0, 'y': 0},
                text        = 'Description:'
            )
            routine_grid.add_widget(_label)

            desc_field      = TextInput(
                size_hint   = [0.70, 0.30],
                pos_hint    = {'x': 0, 'y': 0},
            )
            routine_grid.add_widget(desc_field)
            admin._manage_rout_elem['description'] = desc_field

            # ===============================
            #       Yet another grid
            # ===============================
            inner_grid_container                    = BGFloatLayout(
                size_hint                           = [0.36, 0.36],
                pos_hint                            = {'x': 0, 'y': 0.12}
            )
            inner_grid_container.bg_color.rgba      = [0.5, 0.5, 0.5, 1]
            inner_grid_container.border_color.rgba  = [0, 0, 0, 1]
            inner_grid_container.border_size        = 2
            right_layout.add_widget(inner_grid_container)
            inner_cabaret                           = BGFloatLayout(
                size_hint                           = [1.0, 0.25],
                pos_hint                            = {'x': 0, 'top': 1}
            )
            inner_cabaret.bg_color.rgba             = [0.25, 0.25, 0.25, 1]
            inner_grid_container.add_widget(inner_cabaret)
            inner_label                             = Label(
                text                                = 'Exercises:',
                pos_hint                            = {'x': 0, 'y': 0},
                size_hint                           = [1.0, 1.0],
            )
            inner_cabaret.add_widget(inner_label)
            inner_scroll_container                  = FloatLayout(
                size_hint                           = [1, 0.75],
                pos_hint                            = {'x': 0, 'y': 0}
            )
            inner_grid_container.add_widget(inner_scroll_container)
            inner_scroll                            = ScrollView(
                size_hint                           = [1.0, None],
                pos_hint                            = {'x': 0, 'y': 0},
                do_scroll_y                         = True,
            )
            inner_scroll_container.add_widget(inner_scroll)
            inner_scroll_container.bind(height      = inner_scroll.setter('height'))
            inner_grid                              = GridLayout(
                cols                                = 1,
                size_hint                           = [1.0, None],
                pos_hint                            = {'x': 0, 'y': 0}
            )
            inner_scroll.add_widget(inner_grid)
            inner_grid.bind(minimum_height          = inner_grid.setter('height'))
            admin._manage_rout_elem['inner_grid']   = inner_grid
            dropdown                                = DropdownOption(
                size_hint                           = [0.36, 0.50],
                button_hint_y                       = 0.20,
                option_height                       = 40,
                title                               = 'Add Exercise',
                pos_hint                            = {'x': 0, 'top': 0.10},
                list_position                       = 'up',
                disabled                            = True,
            )
            right_layout.add_widget(dropdown)
            admin._manage_rout_elem['dropdown']     = dropdown
            dropdown.on_selection_made              = admin.on_create_exercise
            # ========================================
            #       Exercise List added, work on
            #       exercise details.
            # ========================================
            exer_detail_layout                      = BGFloatLayout(
                size_hint                           = [0.60, 0.36],
                pos_hint                            = {'right': 1, 'y': 0.12}
            )
            exer_detail_layout.bg_color.rgba        = [0.5, 0.5, 0.5, 1]
            exer_detail_layout.border_color.rgba    = [0, 0, 0, 1]
            exer_detail_layout.border_size          = 2
            right_layout.add_widget(exer_detail_layout)
            exer_detail_grid                        = GridLayout(
                cols                                = 2,
                size_hint                           = [0.80, 0.40],
                spacing                             = 5,
                pos_hint                            = {'x': 0.04, 'center_y': 0.5}
            )
            exer_detail_layout.add_widget(exer_detail_grid)
            exer_detail_grid.add_widget(Label(
                text        = 'Reps:',
                font_size   = 14,
            ))
            exer_detail_grid.add_widget(IntInput(
            ))
            admin._manage_rout_elem['reps'] = exer_detail_grid.children[0]
            exer_detail_grid.add_widget(Label(
                text        = 'Sets:',
                font_size   = 14,
            ))
            exer_detail_grid.add_widget(IntInput(
            ))
            admin._manage_rout_elem['sets'] = exer_detail_grid.children[0]
            # ========================================
            #       Finally, exercise drop-down.
            # ========================================
            exer_dropdown                   = DropdownOption(
                size_hint                   = [0.56, 0.90],
                button_hint_y               = 0.20,
                option_height               = 40,
                title                       = 'Change Exercise',
                pos_hint                    = {'right': 0.96, 'center_y': 0.5},
                font_size                   = 18,
                disabled                    = True,
            )
            exer_detail_layout.add_widget(exer_dropdown)
            admin._manage_rout_elem['change_dropdown'] = exer_dropdown
            exer_dropdown.on_selection_made            = admin.on_change_exercise
            # Add Save Button
            save_btn                        = Button(
                size_hint                   = [0.144, 0.08],
                pos_hint                    = {'right': 1, 'y': 0},
                text                        = 'Save'
            )
            right_layout.add_widget(save_btn)
            def req_update(instance):
                nonlocal admin
                # instance            = admin._manage_params['exercise']
                # exercise            = instance.exercise if instance else None
                instance                    = admin._manage_params['exercise']
                routine                     = admin._manage_params['routine']
                if routine is not None:
                    routine.routine_name        = admin._manage_rout_elem['name'].text
                    routine.routine_description = admin._manage_rout_elem['description'].text
                exercise                    = instance.exercise if instance else None
                
                if exercise is not None:
                    # exercise.reps   = int(admin._manage_rout_elem['reps'].text)
                    # exercise.sets   = int(admin._manage_rout_elem['sets'].text)
                    exercise.reps               = int(admin._manage_rout_elem['reps'].text)
                    exercise.sets               = int(admin._manage_rout_elem['sets'].text)
                    print(f"Changes saved to exercise ({hex(id(exercise))})={exercise.name}")
                    
                # Successful save popup
                success_popup = Popup(title='Success',
                                    content=Label(text='Routine successfully saved.'),
                                    size_hint=(None, None), size=(300, 200))
                success_popup.open()
                admin.rout_list.update()
                admin.rout_list.update(exercise)

            save_btn.bind(on_release = req_update)
            # Add exercise list
            for exercise in admin.exer_list.extract_list():
                dropdown.add_option(exercise.name).exercise         = exercise
                exer_dropdown.add_option(exercise.name).exercise    = exercise
        left_layout_elements(admin, left_layout)
        right_layout_elements(admin, right_layout)


        #   ====================================
        #             Handle Visibility
        #   ====================================
        last_tab    = None
        def on_tab_update(tab_panel, value):
            nonlocal tab, admin, last_tab
            if (value == tab) and (last_tab != tab):
                admin.draw_routine_table()
            elif (value != tab) and (last_tab == tab):
                admin.clear_routine_table(clear_data = True)
            last_tab    = value

        tab_panel.bind(current_tab = on_tab_update)
        return tab
    
class AdminDashboard(Screen):
    def __init__(self, **kwargs):
        self.app            = kwargs.pop('app', None)
        self.exer_list      = kwargs.pop('exer_list', None)
        self.rout_list      = kwargs.pop('rout_list', None)
        self.popup          = kwargs.pop('popup', None)
        self.app_data       = kwargs.pop('app_data', {})
        self._last_routine  = None
        self._image_src     = ""

        super().__init__(**kwargs)
        
        # Main layout
        layout              = FloatLayout(size=(300, 300))
        self.add_widget(layout)

        # Background
        bg                  = Image(source=app_config.app['bg_logo'], fit_mode="fill")
        layout.add_widget(bg)
        
        # Tabbed Panel
        tab_panel           = TabbedPanel(
            pos_hint        = {'center_x': 0.5,'center_y': 0.42},
            size_hint       = (0.8, 0.72),
            do_default_tab  = False,
            tab_width       = 200
        )
        layout.add_widget(tab_panel)
        
        # Tab 1: Add Exercises
        self.create_tab(ExerciseTabs.add_exercise_tab, tab_panel)
        # Tab 2: Add Routine
        self.create_tab(RoutineTabs.add_routine_tab, tab_panel)
        # Tab 3: Manage Exercises
        self.create_tab(ExerciseTabs.manage_exercise_tab, tab_panel)
        # Tab 4: Manage Routine
        self.create_tab(RoutineTabs.manage_routine_tab, tab_panel)
        
        # Back Button
        back_btn = Button(text="Back", size_hint=(None, None), size=(100, 50), pos_hint={'right': 1, 'y': 0})
        back_btn.bind(on_press=self.back_btn_pressed)
        layout.add_widget(back_btn)

        # back_btn   = Button(
        #     text                = 'BACK',
        #     font_name           = admin_config.font_name[2],
        #     font_size           = admin_config.font_size[1],
        #     background_normal   = user_config.button_params['bg_normal'],
        #     background_color    = user_config.button_params['bg_color'],
        #     color               = user_config.button_params['color'],
        #     size_hint           = (10, 50), 
        #     pos_hint            = {'right': 1, 'y': 0}
        # )
        # back_btn.bind(on_press=self.back_btn_pressed)
        # layout.add_widget(back_btn)
    
    def create_tab(self, fun, tab_panel: TabbedPanel):
        tab_item    = fun(self, tab_panel)
        tab_panel.add_widget(tab_item)

     # ===================================
    #       on_ methods added for
    #       the upload image button
    # ===================================
    def on_button_pos(self, instance, pos):
        if not hasattr(instance, 'rect'):
            return
        instance.rect.pos   = pos
    def on_button_size(self, instance, size):
        if not hasattr(instance, 'rect'):
            return
        instance.rect.size   = size

    def open_file_chooser(self, instance):
        import os
        file_chooser    = FileChooserIconView(
            filters     = ["*.png"],
            path        = os.getcwd(),
        )
        file_chooser.bind(on_submit=self.on_file_selection)
        popup               = Popup(title="Select an Image", content=file_chooser, size_hint=(None, None), size=(400, 400))
        self._active_popup  = popup
        popup.open()
    def on_file_selection(self, instance, selection, touch):
        if selection:
            # Update the image source with the selected file
            selected_image_path             = selection[0]
            self.upload_image_btn.source    = self._image_src   = selected_image_path
            self._active_popup.dismiss()
            self._active_popup              = None
        else:
            self.upload_image_btn.source    = app_config.path['icons']['exercise']
    
    def on_add_exer_text_clear(self, *args):
        self._name.text                 = ""
        self._reps.text                 = ""
        self._sets.text                 = ""
        self._dur.text                  = ""
        self._desc.text                 = ""
        self._image_src                 = ""
        self.upload_image_btn.source    = app_config.path['icons']['exercise']

    def add_rout_check_send(self, *args):
        rout_elements   = self._routine_elements
        enable_click    = ((len(rout_elements['grid'].children) > 0) and
                           (rout_elements['name'].text != '') and
                           (rout_elements['description'].text != ''))
        rout_elements['send'].disabled    = not enable_click

    def add_rout_check_submit(self, *args):
        rout_elements   = self._routine_elements
        enable_click    = ((rout_elements['exercise'].selection is not None) and
                           ((rout_elements['reps'].text != '') and (int(rout_elements['reps'].text) > 0)) and
                           ((rout_elements['sets'].text != '') and (int(rout_elements['sets'].text) > 0)))
        rout_elements['submit'].disabled    = not enable_click

    def add_rout_check(self, *args):
        self.add_rout_check_send()
        self.add_rout_check_submit()
    
    def clear_panel_values(self):
        if not hasattr(self, '_exer_fields'):
            return
        exer_fields     = self._exer_fields
        exer_fields['reps'].text        = ""
        exer_fields['sets'].text        = ""
        exer_fields['duration'].text    = ""
        exer_fields['description'].text = ""
    def draw_exercise_widgets(self):
        if not hasattr(self, '_exercise_box'):
            return
        box                 = self._exercise_box
        box.clear_widgets()
        
        exer_list           = self.exer_list.extract_list()
        for exercise in exer_list:
            exer_btn        = ToggleButton(
                group       = 'exercises',
                text        = exercise.name
            )
            
            box.add_widget(exer_btn)
            def option_factory(exer_btn, self, exercise):
                def on_option_click(instance, *args):
                    exer_panel, exer_fields = self._exer_panel, self._exer_fields
                    if instance.state == 'normal':
                        if not exer_panel.hidden:
                            out_anim            = Animation(
                                size_hint_x     = 0,
                                opacity         = 0,
                                d               = 0.25,
                                t               = 'linear'
                            )
                            out_anim           &= Animation(
                                size_hint_y     = 0,
                                d               = 0.25,
                                t               = 'in_quart'
                            )
                            out_anim.start(exer_panel)
                            self.clear_panel_values()
                        exer_panel.hidden       = True
                        self._cur_exercise      = None
                        return
                    
                    # Option selected.
                    if exer_panel.hidden:
                        _size_hint              = app_config.admin_page['exercise_manager']['panel_layout_size']
                        in_anim                 = Animation(
                            size_hint_x         = _size_hint[0],
                            opacity             = 1,
                            d                   = 0.25,
                            t                   = 'linear'
                        )
                        in_anim                &= Animation(
                            size_hint_y         = _size_hint[1],
                            d                   = 0.25,
                            t                   = 'in_quart'
                        )
                        in_anim.start(exer_panel)
                    exer_panel.hidden           = False
                    self._cur_exercise          = exercise
                    # Update parameter values
                    exer_fields['reps'].text        = str(exercise.reps)
                    exer_fields['sets'].text        = str(exercise.sets)
                    exer_fields['duration'].text    = str(exercise.duration)
                    exer_fields['description'].text = exercise.description
                exer_btn.bind(on_release = on_option_click)
            option_factory(exer_btn, self, exercise)
        if not hasattr(self, '_exer_panel'):
            return
        exer_panel              = self._exer_panel
        exer_panel.size_hint    = [0, 0]
        exer_panel.opacity      = 0
        exer_panel.hidden       = True
    def draw_table(self):
        table               = self._table 
        # Name input.
        table.add_widget(Label(text="Name of Exercise:", height=30))
        self._name          = TextInput(multiline=False, height=30)
        table.add_widget(self._name)
        # Repetitions input.
        table.add_widget(Label(text="Reps:"))
        self._reps          = IntInput(multiline=False)
        table.add_widget(self._reps)
        # Sets input.
        table.add_widget(Label(text="Sets:"))
        self._sets          = IntInput(multiline=False)
        table.add_widget(self._sets)
        # Duration input.
        table.add_widget(Label(text="Duration:"))
        self._dur           = IntInput(multiline=False)
        table.add_widget(self._dur)
        # Description input.
        table.add_widget(Label(text="Description:"))
        self._desc          = TextInput()
        table.add_widget(self._desc)
    
    # Implemented for self._manage_rout_elem['dropdown']
    def on_create_exercise(self, instance, selection):
        if selection is None:
            return
        
        dropdown                    = self._manage_rout_elem['dropdown']
        exercise                    = self.exer_list.get_exercise(selection.text).copy()
        cur_routine: RoutineDetails = self._manage_params['routine']
        cur_routine                 = cur_routine.routine if cur_routine else None
       
        if cur_routine is None:
            return
        cur_routine.add_exercise(exercise)
        
        # Add new exercise to grid
        inner_grid                  = self._manage_rout_elem['inner_grid']
        # self.create_exercise_button(inner_grid, exercise)
        self.create_exercise_button(inner_grid, cur_routine, exercise)
        Clock.schedule_once(dropdown.clear_option, -1)
    def on_select_exercise(self, instance):
        prev_instance                           = self._manage_params['exercise']
        self._manage_params['prev_exercise']    = prev_instance
        if instance.state == 'normal':
            self._manage_params['exercise']     = None
        else:
            self._manage_params['exercise']     = instance
        prev_exercise                           = prev_instance.exercise if prev_instance else None
        cur_exercise                            = instance.exercise
        change_dropdown: DropdownOption         = self._manage_rout_elem['change_dropdown']
        change_dropdown.disabled                = instance.state == 'normal'
        if (prev_exercise is not None) and (prev_exercise != cur_exercise):
            prev_exercise.reps  = int(self._manage_rout_elem['reps'].text)
            prev_exercise.sets  = int(self._manage_rout_elem['sets'].text)
        if change_dropdown.disabled:
            change_dropdown.clear_option()
        else:
            change_dropdown.select_option(cur_exercise.name)
            self._manage_rout_elem['reps'].text = str(cur_exercise.reps)
            self._manage_rout_elem['sets'].text = str(cur_exercise.sets)
    def on_change_exercise(self, dropdown, selection):
        instance                        = self._manage_params['exercise']
        cur_exercise: ExerciseDetails   = instance.exercise if instance else None
        if selection is None:
            # print("Disabling fields")
            self._manage_rout_elem['reps'].text     = \
            self._manage_rout_elem['sets'].text     = ""
            self._manage_rout_elem['reps'].disabled = \
            self._manage_rout_elem['sets'].disabled = True
            return
        self._manage_rout_elem['reps'].disabled     = \
        self._manage_rout_elem['sets'].disabled     = False
        base_exercise                               = self.exer_list.get_exercise(selection.exercise.name)
        cur_exercise.inherit(base_exercise)
        instance.text                               = cur_exercise.name
    def on_delete_exercise(self, instance):
        cur_routine: RoutineDetails     = self._manage_params['routine']
        cur_routine                     = cur_routine.routine if cur_routine else None
        cur_option                      = instance.parent
        cur_exercise: ExerciseDetails   = instance.exercise
        inner_grid                      = self._manage_rout_elem['inner_grid']
        # print(f"Current routine: {cur_routine.routine_name}")
        # print(f"Current exercise: {cur_exercise.name}")
        cur_routine.remove_exercise(cur_exercise)
        if self._manage_params['exercise']  == instance:
            change_dropdown: DropdownOption = self._manage_rout_elem['change_dropdown']
            change_dropdown.clear_option()
            self._manage_params['exercise'] = None
        inner_grid.remove_widget(cur_option)
        
    def on_routine_click(self, instance):
        if not hasattr(instance, 'routine'):
            self.manage_routine_fill_exercises(None)
            return
        
        routine                             = instance.routine if instance.state == 'down' else None
        prev_routine                        = self._manage_params['routine']
        self._manage_params['prev_routine'] = prev_routine
        self._manage_params['routine']      = instance if routine else None
        if prev_routine is not None:
            prev_routine.text                   = self._manage_rout_elem['name'].text
            prev_routine                        = prev_routine.routine
            prev_routine.routine_name           = self._manage_rout_elem['name'].text
            prev_routine.routine_description    = self._manage_rout_elem['description'].text
        self.manage_routine_fill_exercises(routine)
    def create_exercise_button(self, inner_grid, routine: RoutineDetails, exercise: ExerciseDetails):
        grid_entry              = GridLayout(
            cols                = 2,
            rows                = 1,
            size_hint           = [1.0, None]
        )
        inner_grid.add_widget(grid_entry)
        grid_entry.exer_button  = ToggleButton(
            text                = exercise.name,
            size_hint           = [0.8, None],
            pos_hint            = {'x': 0, 'y': 0},
            group               = inner_grid,
        )
        grid_entry.add_widget(grid_entry.exer_button)
        grid_entry.exer_button.exercise         = exercise
        grid_entry.exer_button.routine          = routine
        grid_entry.exer_button.bind(on_release  = self.on_select_exercise)
        grid_entry.del_button   = ImageButton2(
            size_hint           = [0.2, None],
            pos_hint            = {'x': 0, 'y': 0},
            source              = app_config.path['icons']['delete'],
        )
        grid_entry.del_button.exercise          = exercise
        grid_entry.del_button.bind(on_release   = self.on_delete_exercise)
        grid_entry.add_widget(grid_entry.del_button)
    def manage_routine_fill_exercises(self, routine: RoutineDetails):
        rout_elements                       = self._manage_rout_elem
        if routine is None:
            self.clear_routine_table()
            self._last_routine              = routine
            return
        if self._last_routine == routine:
            return
        rout_elements['name'].text          = routine.routine_name
        rout_elements['description'].text   = routine.routine_description
        rout_elements['dropdown'].disabled  = False
        inner_grid                          = rout_elements['inner_grid']
        inner_grid.clear_widgets()
        for exercise in iter(routine):
            # self.create_exercise_button(inner_grid, exercise)
            self.create_exercise_button(inner_grid, routine, exercise)
        self._last_routine                  = routine
    def clear_routine_table(self, clear_data: bool = True):
        rout_elements                       = self._manage_rout_elem
        rout_elements['name'].text          = rout_elements['description'].text = ""
        inner_grid: GridLayout              = rout_elements['inner_grid']
        inner_grid.clear_widgets()
        rout_elements['dropdown'].disabled  = True
        if clear_data:
            self._last_routine              = None
            self._manage_params['routine']  = None
            self._manage_params['exercise'] = None
    def draw_routine_table(self):
        rout_list       = self.rout_list.extract_list()
        rout_elements   = self._manage_rout_elem
        if (len(rout_list) == 0):
            rout_elements['no_elem_base'].size_hint = [1.0, 1.0]
            rout_elements['no_elem_base'].opacity   = 1
            rout_elements['elem_base'].size_hint    = [0.0, 0.0]
            rout_elements['elem_base'].opacity      = 0
            return
        rout_elements['elem_base'].size_hint        = [1.0, 1.0]
        rout_elements['elem_base'].opacity          = 1
        rout_elements['no_elem_base'].size_hint     = [0.0, 0.0]
        rout_elements['no_elem_base'].opacity       = 0
        # Manage grid objects here.
        grid    = rout_elements['grid']
        grid.clear_widgets()
        for routine in rout_list:
            routine: RoutineDetails
            grid_button         = ToggleButton(
                text            = routine.routine_name,
                pos_hint        = {'x': 0, 'y': 0},
                height          = 80,
                group           = grid,
            )
            grid_button.routine = routine
            grid.add_widget(grid_button)
            grid_button.bind(on_release = self.on_routine_click)
        
    def back_btn_pressed(self, instance):
        self.on_add_exer_text_clear()
        self.clear_routine_table()
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current    = 'main_screen'