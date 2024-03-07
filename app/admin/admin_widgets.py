# Import necessary modules from the Kivy library
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.animation import Animation

# Import various properties and graphics components from Kivy
from kivy.properties import (
    OptionProperty, BooleanProperty, NumericProperty,
    ColorProperty, ListProperty, StringProperty,
    ObjectProperty
)

from kivy.graphics import Rectangle, Color
from kivy.graphics import Color, RoundedRectangle

# Import window management and clock from Kivy
from kivy.core.window import Window
from kivy.clock import Clock

# Import application-specific configuration from 'admin.app_config'
import admin.app_config as app_config

# Define a custom TextInput class that only allows integer input
class IntInput(TextInput):
    def __init__(self, **kwargs):
        super(IntInput, self).__init__(**kwargs)

    # Override the insert_text method to filter non-integer input
    def insert_text(self, substr, from_undo=False):
        try:
            int(substr)
        except ValueError:
            return ""        
        return super(IntInput, self).insert_text(substr, from_undo=from_undo)
    
# Define a custom Label class with left-aligned text
class LeftLabel(Label):
    def __init__(self, **kwargs):
        super(LeftLabel, self).__init__(**kwargs)
        # Set default height if not specified and adjust text alignment
        if (not 'height' in kwargs) and (self.size_hint[1] is None):
            self.height         = 50
            self.size_hint_y    = None
        self.halign             = 'left'
        self.valign             = 'center'

    # Adjust text_size when the size of the label changes
    def on_size(self, instance, size):
        self.text_size      = size

# Define a custom Button with an image background
class ImageButton(ButtonBehavior, Image):
    bg_color    = ColorProperty([0.5, 0.5, 0.5, 1])
    bg_normal   = ColorProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Change the color on button press
    def on_press(self):
        self.color  = self.bg_color

    # Change the color back on button release
    def on_release(self):
        self.color  = self.bg_normal

# Define another custom ImageButton with toggle behavior
class ImageButton2(ToggleButtonBehavior, Image):
    hovered         = BooleanProperty(False)
    focus_counter   = NumericProperty(0)

    def __init__(self, **kwargs):
        super(ImageButton2, self).__init__(**kwargs)
        self.always_release     = True
        self.prev_state         = self.state

        with self.canvas:
            self._color         = Color(0, 0, 0, 0)
            self._color_rect    = Rectangle(
                pos             = self.pos,
                size            = self.size,
            )

    # Increment focus counter on press
    def on_press(self, *args):
        self.focus_counter   += 1

    # Decrement focus counter on release
    def on_release(self, *args):
        self.focus_counter   -= 1

    # Update the color based on the focus counter
    def on_focus_counter(self, instance, counter):
        if counter > 0:
            self._color.rgba[3] = 0.35
        else:
            self._color.rgba[3] = 0
        self.canvas.ask_update()

    # Update the size of the color rectangle when the button size changes
    def on_size(self, instance, size):
        if not hasattr(self, '_color_rect'):
            return
        self._color_rect.size   = size

    # Update the position of the color rectangle when the button position changes
    def on_pos(self, instance, pos):
        if not hasattr(self, '_color_rect'):
            return
        self._color_rect.pos    = pos

    # Track the state changes and update the focus counter accordingly
    def on_state(self, instance, state):
        if self.state == self.prev_state:
            return
        
        self.prev_state = self.state
        if self.state == 'down':
            self.focus_counter  += 1
        else:
            self.focus_counter  -= 1

# Define a custom FloatLayout with a background color and border
class BGFloatLayout(FloatLayout):
    def __init__(self, **kwargs):
        self.border_size        = 0

        super(BGFloatLayout, self).__init__(**kwargs)
        with self.canvas:
            self.border_color       = Color(1,1,1,1)
            self.border_rect        = Rectangle(pos=self.pos, size=self.size)
            self.bg_color           = Color(0,0,0,1)
            self.bg_rect            = Rectangle(pos=self.pos, size=self.size)

    # Update the position of the background and border rectangles when the layout position changes
    def on_pos(self, instance, pos):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos            = pos
        if hasattr(self, 'border_rect'):
            self.border_rect.pos        = [pos[0] - self.border_size,
                                           pos[1] - self.border_size]
            
    # Update the size of the background and border rectangles when the layout size changes
    def on_size(self, instance, size):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.size           = size
        if hasattr(self, 'border_rect'):
            self.border_rect.size       = [size[0] + 2*self.border_size,
                                           size[1] + 2*self.border_size]
            
# Define a custom Button with rounded corners
class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (1, 1, 1, 1)  # Default white background

        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])

        self.bind(pos=self.update_rect, size=self.update_rect)

    # Update the position and size of the rounded rectangle when the button position or size changes
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# Define a custom Button with background colors for different states
class BGButton(Button):
    bg_color            = ColorProperty([0.5, 0.5, 0.5, 0.0])
    bg_down_color       = ColorProperty([0.4, 0.4, 0.4, 0.8])
    bg_disabled         = ColorProperty([0.4, 0.4, 0.4, 0.0])
    bg_down_disabled    = ColorProperty([0.3, 0.3, 0.3, 0.4])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color               = [1.0, 1.0, 1.0, 0.0]
        self.background_normal              = ""
        self.background_down                = ""
        self.background_disabled_normal     = ""
        self.background_disabled_down       = ""
        self.halign                         = "center"
        self.valign                         = "middle"
        self.bind(background_color          = self._request_update)
        self.bind(size                      = self.setter("text_size"))
    
    # Adjust background color on button press
    def on_press(self):
        if self.disabled:
            self.background_color   = self.bg_down_disabled
        else:
            self.background_color   = self.bg_down_color

    # Adjust background color back on button release
    def on_release(self):
        if self.disabled:
            self.background_color   = self.bg_disabled
        else:
            self.background_color   = self.bg_color

    # Request a canvas update when the background color changes
    def _request_update(self, instance, listvalue):
        self.canvas.ask_update()

    # Update background color based on state and whether the button is disabled
    def on_bg_color(self, instance, color):
        if (self.state == 'normal') and (not self.disabled):
            self.background_color   = self.bg_color

    def on_bg_down_color(self, instance, color):
        if (self.state == 'down') and (not self.disabled):
            self.background_color   = self.bg_down_color

    def on_bg_disabled(self, instance, color):
        if (self.state == 'normal') and (self.disabled):
            self.background_color   = self.bg_disabled

    def on_bg_down_disabled(self, instance, color):
        if (self.state == 'down') and (self.disabled):
            self.background_color   = self.bg_down_disabled

# Define a custom FloatLayout for a widget representing an exercise in a routine
class RoutineExerWidget(BGFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set background color and border size based on app configuration
        self.bg_color.rgba  = app_config.admin_page['routine_manager']['bg_color']
        self.border_size    = 2

         # Create a content FloatLayout within the main layout
        self._content       = FloatLayout(
            size_hint       = [0.90, 0.90],
            pos_hint        = {'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(self._content)

        # ===========================
        #       Left-side content
        # ===========================
        left_layout             = GridLayout(
            size_hint           = [0.40, 1.0],
            pos_hint            = {'x': 0, 'y': 0},
            cols                = 1,
            row_default_height  = 25,
            row_force_default   = True
        )
        self._content.add_widget(left_layout)

        exer_label              = LeftLabel(
            text                = "Exercise:",
            font_size           = 16,
            height              = 25
        )
        left_layout.add_widget(exer_label)

        self.exer_button        = ToggleButton(
            text                = "-- List --",
            font_size           = 16,
            group               = 'exercise_select_group',
        )
        left_layout.add_widget(self.exer_button)

        # ===========================
        #       Right-side content
        # ===========================
        right_layout            = GridLayout(
            size_hint           = [0.55, 0.90],
            pos_hint            = {'x': 0.45, 'center_y': 0.5},
            cols                = 2,
            row_default_height  = 25,
            row_force_default   = True,
        )
        self._content.add_widget(right_layout)
        # self._content.bind(size = self.on_content_size)

        right_layout.add_widget(LeftLabel(text = "Reps:", font_size = 16, height = 20))
        right_layout.add_widget(IntInput(text = "10", font_size = 12))
        right_layout.add_widget(LeftLabel(text = "Sets:", font_size = 16, height = 20))
        right_layout.add_widget(IntInput(text = "2", font_size = 12))
    # Bind click and release events to specified callback functions
    def bind(self, **kwargs):
        click_callback      = kwargs.pop('on_click', None)
        release_callback    = kwargs.pop('on_release', None)

        if click_callback:
            self.exer_button.bind(on_click      = click_callback)
        if release_callback:
            self.exer_button.bind(on_release    = release_callback)

        super().bind(**kwargs)
    # Unbind click and release events from specified callback functions
    def unbind(self, **kwargs):
        click_callback      = kwargs.pop('on_click', None)
        release_callback    = kwargs.pop('on_release', None)
        
        if click_callback:
            self.exer_button.unbind(on_click  = click_callback)
        if release_callback:
            self.exer_button.unbind(on_release  = release_callback)

        super().unbind(**kwargs)

# Define a custom dropdown option widget
class DropdownOption(FloatLayout):
    # Define various properties for the dropdown option
    scroll_size_hint    = ListProperty([1.0, 1.0])
    title               = StringProperty("")
    anim_dur            = NumericProperty(0.25, min = 0.001, errorvalue = 0.25)
    button_hint_y       = NumericProperty(0.12, max = 1, min = 0, errorvalue = 0.12)
    option_height       = NumericProperty(25, min = 10, errorvalue = 10)
    option_space        = NumericProperty(0, min = 0, errorvalue = 0)
    font_size           = NumericProperty(12, min = 1, errorvalue = 1)
    _show_counter       = NumericProperty(1)
    _was_hidden         = BooleanProperty(False)
    disabled            = BooleanProperty(False)
    selection           = ObjectProperty(None, allownone = True)
    list_position       = OptionProperty('down', options=('down', 'up'))

    # Constructor for the dropdown option widget
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create a toggle button as the main button of the dropdown
        self._button                    = ToggleButton(
            text                        = self.title,
            size_hint                   = [1.0, self.button_hint_y],
            pos_hint                    = {'x': 0, 'top': 1.0},
            font_size                   = self.font_size,
        )
        self.add_widget(self._button)
        self._button.bind(on_release    = self.on_release)

        dy                              = 1 - self.button_hint_y
        self._drop_container            = FloatLayout(
            size_hint                   = [1.0, dy],
            pos_hint                    = {'x': 0, 'top': dy}
        )
        self.add_widget(self._drop_container)

        self._container                 = BGFloatLayout(
            size_hint                   = self.scroll_size_hint,
            pos_hint                    = {'center_x': 0.5, 'center_y': 0.5},
        )
        self._drop_container.add_widget(self._container)
        self._container.bg_color.rgba   = [0.2, 0.2, 0.2, 1]

        self._scroll                    = ScrollView(
            size_hint                   = [1.0, None],
            pos_hint                    = {'x': 0, 'y': 0},
            do_scroll_y                 = True,
        )
        self._container.add_widget(self._scroll)
        self._container.bind(height     = self._scroll.setter("height"))

        self._grid                      = GridLayout(
            cols                        = 1,
            size_hint                   = [1.0, None],
            pos_hint                    = {'x': 0, 'y': 0},
            row_default_height          = self.option_height,
            row_force_default           = True,
            spacing                     = [0, self.option_space]
        )
        self._scroll.add_widget(self._grid)
        self._grid.bind(minimum_height  = self._grid.setter("height"))

        # Trigger self.on__show_counter()
        self._update_button_state()
        self.on_list_position(self, self.list_position)
        self._show_counter              = 0

    def _update_button_state(self):
        if not hasattr(self, '_button'):
            return
        self._button.disabled           = self.disabled or (len(self._grid.children) < 1)

    # =====================================
    #       On property change functions
    # =====================================

    # Update the size_hint of the container based on the scroll_size_hint property
    def on_scroll_size_hint(self, instance, size_hint):
        if not hasattr(self, '_container'):
            return
        self._container.size_hint   = size_hint

    # Update the title text when the title property changes
    def on_title(self, instance, value):
        if not hasattr(self, '_button'):
            return
        if self.selection is not None:
            return
        self._button.text   = value

    # Handle the show counter property changes
    def on__show_counter(self, instance, counter):
        if not hasattr(self, '_drop_container'):
            return

        if (counter <= 0) and (not self._was_hidden):
            self._was_hidden    = True
            self.anim           = Animation(
                size_hint_y     = 0.0,
                opacity         = 0,
                duration        = self.anim_dur,
                transition      = 'in_sine')
            self.anim.start(self._drop_container)

        elif (counter == 1) and (self._was_hidden):
            self._was_hidden    = False
            dy                  = 1 - self.button_hint_y
            self.anim           = Animation(
                size_hint_y     = dy,
                opacity         = 1,
                duration        = self.anim_dur,
                transition      = 'out_sine')
            self.anim.start(self._drop_container)

    # Handle the selection property changes
    def on_selection(self, instance, value):
        if value is None:
            self._button.text   = self.title
        else:
            self._button.text   = self.selection.text

    # Handle the list_position property changes
    def on_list_position(self, instance, value):
        if not hasattr(self, '_drop_container'):
            return
        
        if value == 'down':
            dy  = 1 - self.button_hint_y
            self._drop_container.pos_hint   = {'x': 0, 'top': dy}

        elif value == 'up':
            self._drop_container.pos_hint   = {'x': 0, 'y': 1}

    # Handle the disabled property changes
    def on_disabled(self, instance, state):
        self._update_button_state()

    # Handle the font_size property changes
    def on_font_size(self, instance, size):
        if not hasattr(self, '_button'):
            return
        self._button.font_size  = size

    # Handle the button press event
    def on_release(self, instance):
        self.show(not self.shown())

    # Placeholder for selection made event
    @staticmethod
    def on_selection_made(self, instance):
        pass

    # Handle the option release event
    def on_option_release(self, instance):
        self._button.state  = "normal"
        self.show(not self.shown())
        if self.selection == instance:
            instance.state  = "normal"
            self.selection  = None
        else:
            self.selection  = instance
        self.on_selection_made(self, self.selection)

    # Common method to show or hide the dropdown based on a flag
    def show(self, flag: bool = True, toggle: bool = True):
        if toggle:
            self._show_counter  = 1 if flag else 0
        else:
            inc                 = 1 if flag else -1
            self._show_counter += inc

    # Check if the dropdown is currently shown
    def shown(self):
        return self._show_counter > 0

    # Add an option to the dropdown
    def add_option(self, opt_text: str = "") -> ToggleButton:
        option                  = ToggleButton(
            size_hint           = [1.0, None],
            height              = self.option_height,
            pos_hint            = {'x': 0, 'y': 0},
            text                = opt_text,
            group               = self
        )
        if self.list_position == 'up':
            self._grid.add_widget(option, -1)
        else:
            self._grid.add_widget(option)
        option.bind(on_release  = self.on_option_release)
        self._update_button_state()
        return option

    # Remove an option from the dropdown
    def remove_option(self, opt_text: str = ""):
        _option = None
        for option in self._grid.children:
            if option.text == opt_text:
                _option = option
                break
        
        if not _option:
            return
        
        if self.selection  == _option:
            self.selection  = None
        self._grid.remove_widget(_option)

    # Get the text of the currently selected option
    def get_option(self) -> str:
        return self.selection.text if (self.selection is not None) else ""
    
    # Set the text of the currently selected option
    def set_option(self, opt_text: str):
        if self.selection is None:
            return
        self.selection.text         = opt_text

    # Clear the currently selected option
    def clear_option(self, *args):
        if self.selection is not None:
            self.selection.state    = 'normal'
        self.selection              = None
        self.on_selection_made(self, self.selection)

    # Select an option by its text
    def select_option(self, opt_text: str):
        for option in self._grid.children:
            if option.text == opt_text:
                self.selection      = option
                self.on_selection_made(self, self.selection)
                return True
        else:
            return False
        
# Define a class for an admin popup    
class AdminPopup:
    def __init__(self, **kwargs):
        self.popup              = Popup(**kwargs)
        self.popup.size_hint    = (None, None)
        self.popup.size         = (360, 240)

        content                 = FloatLayout(size=self.popup.size)

         # Create Label text:
        body_text               = Label(
            size_hint           = [1.0, 0.8],
            pos_hint            = {'x': 0.0, 'y': 0.2},
            valign              = 'top',
            halign              = 'left',
        )
        content.add_widget(body_text)

        def on_body_text_size(instance, size):
            instance.text_size  = size
        body_text.text_size     = body_text.size
        body_text.bind(size=on_body_text_size)

        self._body_text         = body_text

        # Create container for Confirm and Cancel buttons
        btn_container           = GridLayout(size_hint=[1.0, 0.2], cols=2, pos_hint={'x': 0, 'y': 0})
        content.add_widget(btn_container)

        # Create confirm and cancel buttons
        confirm_button          = Button(text="Confirm")
        cancel_button           = Button(text="Cancel")
        self._confirm           = confirm_button
        btn_container.add_widget(confirm_button)
        btn_container.add_widget(cancel_button)

        cancel_button.bind(on_release=self.popup.dismiss)
        self.popup.content      = content

    # Get the body text of the popup
    def get_body_text(self) -> str:
        return self._body_text.text
    
    # Set the body text of the popup
    def set_body_text(self, value: str):
        self._body_text.text    = value

    # Get the confirm button of the popup
    def get_confirm_button(self):
        return self._confirm

    # Open the popup
    def open(self):
        self.popup.open()

# Define the main AppHandler class
class AppHandler(App):
    aspect_ratio    = NumericProperty(1.0)

    # Initialize the AppHandler class
    def __init__(self, **kwargs):
        super(AppHandler, self).__init__(**kwargs)

        self._watcher   = Clock.schedule_interval(
            self.update_aspect_ratio,
            0,
        )

    # Update the aspect ratio property based on the window dimensions
    def update_aspect_ratio(self, *args):
        self.aspect_ratio       = AppHandler.get_raw_aspect_ratio()

    # Get the raw aspect ratio based on the window dimensions
    def get_raw_aspect_ratio():
        width, height           = Window.width, Window.height
        if height == 0:
            aspect_ratio        = 100.0
        else:
            aspect_ratio        = width / height
        return aspect_ratio