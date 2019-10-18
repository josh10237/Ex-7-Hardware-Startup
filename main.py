import os
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix import slider
from kivy.uix.screenmanager import ScreenManager, Screen

from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton
import spidev
from time import sleep
import RPi.GPIO as GPIO
from pidev.stepper import stepper

spi = spidev.SpiDev()

spd = 400
dir = 1

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
IMAGE_SCREEN_NAME = 'image_screen'
ADMIN_SCREEN_NAME = 'admin'
STANFORD_SCREEN_NAME = 'stanford_screen'
s0 = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
             steps_per_unit=200, speed=8)
x = False
speed = 10
posCurrent = 0
runningPreset = False


class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER


Window.clearcolor = (1, 1, 1, 1)  # White


class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """

    def togglePressed(self, label):
        toggle = label
        global spd
        global dir
        if toggle == "On":
            self.ids.toggle_text.text = "Off"
            self.MotorOn()
        else:
            self.ids.toggle_text.text = "On"
            s0.softStop()
            s0.free_all()

    def toggleDirPressed(self, label):
        toggle = label
        global spd
        global dir
        if toggle == "Clockwise":
            self.ids.toggle_dir_text.text = "Counter Clockwise"
            dir = 1
        else:
            self.ids.toggle_dir_text.text = "Clockwise"
            dir = 0
        self.MotorOn()

    def MotorOn(self):
        global dir
        global spd
        if self.ids.toggle_text.text == "Off":
            spd = (self.ids.slider.value * 10)
            s0.run(dir, spd)

    def presetPressed(self):
        global posCurrent
        global runningPreset
        s0.set_speed(1)
        s0.start_relative_move(15)
        while s0.is_busy():
            posCurrent = s0.get_position_in_units()
            self.ids.pos_label.text = "Position: " + str(posCurrent)
            sleep(.01)
        sleep(10)
        s0.set_speed(5)
        s0.start_relative_move(10)
        while s0.is_busy():
            posCurrent = s0.get_position_in_units()
            self.ids.pos_label.text = "Position: " + str(posCurrent)
            sleep(.01)
        sleep(8)
        s0.goHome()
        while s0.is_busy():
            posCurrent = s0.get_position_in_units()
            self.ids.pos_label.text = "Position: " + str(posCurrent)
            sleep(.01)
        sleep(30)
        s0.set_speed(8)
        s0.start_relative_move(-100)
        while s0.is_busy():
            posCurrent = s0.get_position_in_units()
            self.ids.pos_label.text = "Position: " + str(posCurrent)
            sleep(.01)
        sleep(10)
        s0.goHome()
        posCurrent = s0.get_position_in_units()
        self.ids.pos_label.text = "Position: " + str(posCurrent)

    def pressed(self):
        """
        Function called on button touch event for button with id: testButton
        :return: None
        """
        PauseScreen.pause(pause_scene_name='pauseScene', transition_back_scene='main', text="Test", pause_duration=5)

    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'


class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(
            ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(
            MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()


"""
Widget additions
"""

Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))

"""
MixPanel
"""


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()