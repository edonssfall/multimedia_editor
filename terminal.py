import shutil
from video_editor import *
from db import *
from keys import *


class Cursor:
    """
    All functional to move between folder + move to home folder
    -d : Show all USB Devices
    /d : Function to chose one USB device and move there
    """

    def __init__(self):
        self.start_direction = os.getcwd()[:os.getcwd()[7:].find('/') + 8]
        self.username = self.start_direction[6:-1]
        self.command = " "
        self.path = str()
        self.cores = os.cpu_count()
        self.videos_list = list()
        self.images_list = list()
        self.db_list = list()
        self.data_base = PostgresSQL_DataBase(dbname, user, password, host, port)

    def __str__(self):
        """
        Show current path how in Terminal
        """
        return f"{os.getcwd()}$ "

    def move(self):
        """
        Move between folders
        """
        self.path = f"{os.getcwd()}/{self.command[self.command.find('cd') + 3:]}/"
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
                os.chdir(self.path)
            except FileNotFoundError or NotADirectoryError or PermissionError:
                self.command = input(f'Enter index of disk or Enter to cancel$ ')

    def basic_location(self):
        """
        Move to home folder
        """
        os.chdir(self.start_direction)
        self.path = os.getcwd()

    def bash_commands(self):
        """
        Bash commands supported by Python_3.10
        """
        os.system(self.command)

    def video_commands(self):
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
            video0 = Video_editor(self.videos_list[0])
            print(
                f"\nName: {video0.folder_name}\n"
                f"Duration: {video0.fps * video0.total_frames}.sec\n"
                f"FPS: {video0.fps}\n"
                f"Resolution: {video0.resolution}\n"
            )
        # Slice video
        elif self.command.startswith('-vs'):
            start_compare = str()
            while start_compare is not int():
                start_compare = int(input(f'Enter beginning of same frames in first video '))
            self.video_cut(start_compare)
            for values in self.db_list:
                self.data_base.insert_db_timing('timing', values[0], values[1], values[2])

    def video_cut(self, start_compare=int(), video_count=0):
        video0 = Video_editor(self.videos_list[video_count])
        for i in range(video_count+1, len(self.videos_list)):
            print(f'Compare video {i+1} (+)')
            time_video1 = video0.fast_video_compare(self.videos_list[i], start_compare)
            duration = time_video1[1] - time_video1[0]
            if duration < 15:
                print(f'Duration is {len(time_video1) * video0.fps}')
                start_compare = str()
                while start_compare is not int():
                    start_compare = int(input(f'Enter sec of start same frames in '
                                              f'{self.videos_list[i]}'))
                self.db_list.append([video0.time[0], video0.duration, video0.folder_name])
                self.video_cut(int(start_compare), i)
                break
            print(f'Slice video {i+1} (+)')
            video = Video_editor(self.videos_list[i])
            video.slice_video([time_video1[0], time_video1[1]])
            self.db_list.append([time_video1[0], video0.duration, video.folder_name])
        self.db_list.append([video0.time[0], video0.duration, video0.folder_name])

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
