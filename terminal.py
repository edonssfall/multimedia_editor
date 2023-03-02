import os
import numpy as np


class Cursor:
    """
    All functional to move between folder + move to home folder
    -d : Show all USB Devices
    /d : Function to chose one USB device and move there
    """

    def __init__(self):
        self.start_direction = os.getcwd()[:os.getcwd()[7:].find('/') + 8]
        self.username = self.start_direction[6:-1]
        self.command = input(self.__str__())
        self.path = f"{os.getcwd()}/{self.command[self.command.find(' ') + 1:]}/"
        self.cores = os.cpu_count()

    def __str__(self):
        """
        Show current path wie in Terminal
        """
        return f"{os.getcwd()}$ "

    def move(self):
        """
        Move between folders
        """
        try:
            os.chdir(self.path)
        except FileNotFoundError:
            print(f"Directory {self.path} does not exist")
        except NotADirectoryError:
            print(f"{self.path} not a directory")
        except PermissionError:
            print(f"You don't have permission to change to {self.path}")

    def hard_driver_list(self):
        """
        -d :Show list of connected devices
        """
        usb_device_array = np.array(os.listdir(f'/media/{self.username}'))
        if usb_device_array is not []:
            for i, disk in enumerate(usb_device_array):
                print(i, disk)
        else:
            print('No usb drivers inserted or mounted')
        return usb_device_array

    def hard_driver_move(self):
        """
        Move to connected device
        Choose device just by its number
        """
        usb_device_array = self.hard_driver_list()
        while self.command not in usb_device_array:
            self.command = input(f"Enter a number of hard driver or Enter to cancel$ ")
            if not self.command.isdigit():
                continue
            try:
                self.command = usb_device_array[int(self.command)]
                self.path = f'/media/{self.username}/{self.command}/'
            except FileNotFoundError or NotADirectoryError or PermissionError:
                self.command = input(f'Enter index of disk or Enter to cancel$ ')
        self.move()

    def basic_location(self):
        """
        Move to home folder
        """
        os.chdir(self.start_direction)

    def bash_commands(self):
        """
        Bash commands supported by Python_3.10
        """
        os.system(self.command)
