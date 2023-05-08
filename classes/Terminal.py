import os
import numpy as np
from platform import system
from dotenv import load_dotenv

from video_system.video_editor import VideoEditor
from classes.DataBase import PostgresSQL_DataBase
from classes.ThreadExecutor import FFMpegThreads

load_dotenv()


class Cursor:
    # TODO: main menu and beautiful func animation
    """
    All functional to move between folder + move to home folder
    -d : Show all USB Devices
    /d : Function to chose one USB device and move there
    """
    def __init__(self):
        self.data_base = PostgresSQL_DataBase(
            dbname=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT']
        )
        self.system = system()
        self.system_usb_path = None
        self.home_direction = os.path.expanduser('~')
        self.username = os.getlogin()
        self.command = " "
        self.path = str()
        self.videos_list = list()
        self.video_slice = dict()

    def __str__(self):
        """
        Show current path how in Terminal
        """
        return f"{os.getcwd()}$ "

    def move(self):
        """
        Move between folders
        """
        # Read path from command
        self.path = os.path.join(os.getcwd(), self.command[self.command.find('cd') + 3:])
        # Try to change folder
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
        # Check what system to use correct path to external drivers
        if self.system == "Windows":
            self.system_usb_path = "/Volumes/"
        elif self.system == "Linux":
            self.system_usb_path = f"/media/{self.username}/"
        elif self.system == "Darwin":
            self.system_usb_path = "/Volumes/"
        # Make list of external driver
        usb_device_array = np.array(os.listdir(self.system_usb_path))
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
        # Easier way to access external driver
        while self.command != "":
            self.command = input(f"Enter a number of hard driver or Enter to cancel> ")
            # Only number to access driver
            if not self.command.isdigit():
                continue
            try:
                self.command = usb_device_array[int(self.command)]
                self.path = os.path.join(self.system_usb_path, self.command)
                os.chdir(self.path)
            except FileNotFoundError or NotADirectoryError or PermissionError:
                self.command = input(f'Enter index of disk or Enter to cancel> ')

    def basic_location(self):
        """
        Move to home folder
        """
        os.chdir(self.home_direction)
        self.path = os.getcwd()

    def bash_commands(self):
        """
        Bash commands supported by Python_3.10
        """
        os.system(self.command)

    def video_cut(self, start_compare=int(), video_count=0):
        # TODO: to make only one func after first to compares
        video0 = VideoEditor(self.videos_list[video_count])
        for i in range(video_count+1, len(self.videos_list)):
            print(f'Work with {self.videos_list[i]}')
            print(f'Compare video(+)')
            time_video1 = video0.main_compare_func(self.videos_list[i], start_compare)
            duration = time_video1[1] - time_video1[0]
            if duration < 15:
                print(f'Duration is {len(time_video1) * video0.fps}')
                start_compare = str()
                while not start_compare.isdigit():
                    start_compare = input(f'Enter sec of start same frames in {self.videos_list[i]}> ')
                self.data_base.insert_db_timing([video0.time[0], video0.duration, video0.short_name])
                self.video_cut(int(start_compare), i)
                break
            video = VideoEditor(self.videos_list[i])
            self.video_slice[video] = [time_video1[0], time_video1[1]]
            self.data_base.insert_db_timing([time_video1[0], duration, video.short_name])
        self.data_base.insert_db_timing([video0.time[0], video0.duration, video0.short_name])

    def video_slicer(self):
        print(f'Slice videos(+)')
        with FFMpegThreads(max_workers=os.cpu_count()) as thread:
            for keys, values in self.video_slice.items():
                thread.add_message([keys, values])
            thread.wait_for_complete()

    def video_commands(self):
        # TODO: make cycle to find only video files
        #  add method to fast check format file
        """
        Make video list to self.videos_list
        :return: one list of all videos in folder
        """
        files_list = sorted(os.listdir())
        for i in range(len(files_list)):
            if os.path.isfile(files_list[i]):
                self.videos_list.append(files_list[i])
        # Video info from first
        if self.command.startswith('-vi'):
            video0 = VideoEditor(self.videos_list[0])
            print(
                f"\nName: {video0.short_name}\n"
                f"Duration: {video0.fps * video0.total_frames}.sec\n"
                f"FPS: {video0.fps}\n"
                f"Resolution: {video0.resolution}\n"
            )
        # Slice video
        elif self.command.startswith('-vs'):
            start_compare = str()
            while not start_compare.isdigit():
                start_compare = input(f'Enter beginning of same frames in first video> ')
            self.video_cut(int(start_compare))
            self.video_slicer()

    def sql_commands(self):
        while self.command != '':
            self.data_base.terminal_to_db()
            self.command = input('SQL helper\n> ')
            if self.command.startswith('-l'):
                self.data_base.get_tables()
            elif self.command.startswith('-h'):
                self.command = input(
                    '-h    Help in SQL\n'
                    '-l    For list of tables\n'
                    '-t    Terminal sql\n'
                    'Enter commands like:\n'
                    'SELECT {line_name} FROM {table_name}\n'
                    'and other SQL commands\n\n'
                )
