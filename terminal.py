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
        self.delete_list = list()
        self.images_list = list()
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
            self.video_slice()

    def video_slice(self, video0_l=0, video1_l=1):
        start_compare = int(input('Enter beginning of same frames in first video in sec '))
        db_list = list()
        while True:
            video0, video1 = Video_editor(self.videos_list[video0_l]), Video_editor(self.videos_list[video1_l])
            start_compare = start_compare * video0.fps
            boards_compare = [0, (video0.total_frames * video0.fps) / 3]  # for auto recognize
            print('First compare of videos        ', end='')
            time_video0, time_video1 = video0.compare_videos(video1.name, start_compare, boards_compare)
            same_duration = time_video0[1] - time_video0[0]

            # If len of same time less than 80 sec
            if same_duration < 80:
                print(f'{video0.folder_name} and {video1.folder_name} not alot frames\n'
                      f'Duration = {same_duration}')
                while True:
                    counter = int()
                    flag_str = input(f'Press Enter to end compare or enter or u can enter new start to compare')
                    for b in flag_str:
                        if b == ' ':
                            counter += 1
                    if counter <= 1:
                        break
                    flag_str = input(f'Must be\n'
                                     f'1     for new start\n'
                                     f'1 2   for new series\n'
                                     f'>')
                if len(flag_str) == 0:
                    break
                elif flag_str.isdigit():
                    start_compare = int(flag_str)
                    continue
                elif len(flag_str) > 1:
                    # Command to skip rerunning
                    if flag_str.startswith('go'):
                        pass
                    else:
                        video0, video1 = int(flag_str[:flag_str.find(' ')]), int(flag_str[flag_str.find(' '):])
                        continue

            print('Processing slicing video 0             ',)
            video0.slice_video(time_video0)
            print('Processing slicing video 1             ',)
            video1.slice_video(time_video1)

            # Add to lists to delete and add info to db
            db_list.append([time_video0[0], same_duration, video0.folder_name])
            db_list.append([time_video1[0], same_duration, video1.folder_name])
            self.delete_list.append(self.videos_list[video0_l])
            self.delete_list.append(self.videos_list[video1_l])

            for i in range(video1_l + 1, len(self.videos_list) + 1):
                video = Video_editor(self.videos_list[i])
                folder_frames = f'{video0.global_path}/{video0.folder_name}'
                print(f'Processing compare frames to video {i} ')
                time_compare = video.compare_frames_to_video(folder_frames, boards_compare)
                self.delete_list.append(self.videos_list[i])
                # If len same time less than 80 sec
                if len(time_compare) < 80 * video0.fps:
                    print(f'Duration is {len(time_compare) * video0.fps}')
                    while True:
                        flag_str = input(f'Press Enter to abort compare or y to make new compare')
                        if len(flag_str) == 0 or i >= len(self.videos_list) + 1:
                            shutil.rmtree(video0.folder_name)
                            break
                        else:
                            if len(flag_str) > 1:
                                # Command to skip rerunning
                                if flag_str.startswith('go'):
                                    pass
                                else:
                                    flag_str = input(f"Example\n"
                                                     f"Only Enter\n"
                                                     f"or\n"
                                                     f"y\n"
                                                     f"> ")
                                    if flag_str == 'y':
                                        shutil.rmtree(video0.folder_name)
                                        self.video_slice(i, i+1)
                                        break
                time_compare = [time_compare[0], time_compare[0] + same_duration]

                print(f'Processing slicing video {i}          ')
                video.slice_video(time_compare)
                db_list.append([time_compare[0], same_duration, video.folder_name])
            break
        shutil.rmtree(video0.folder_name)
        print(db_list)
        print(self.delete_list)

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
