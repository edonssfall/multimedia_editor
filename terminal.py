import numpy as np
import time
import shutil
from video_editor import *


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
        self.path = str()
        self.cores = os.cpu_count()
        self.videos_list = list()
        self.images_list = list()

    def __str__(self):
        """
        Show current path wie in Terminal
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

    def video_slice(self):
        start_time = time.time()
        video0, video1 = Video_editor(self.videos_list[0]), self.videos_list[1]
        start_compare = int(input('Enter beginning of same frames in first video in sec ')) * video0.fps

        print('Processing first compare of 2 videos (+)')
        # Now find only one part
        compa_s = time.time()
        time_video0, time_video1 = video0.compare_videos(video1, start_compare)
        print(time_video0, time_video1)
        same_time_orig, same_time_compare = time_video0[0], time_video1[0]
        print(same_time_orig, same_time_compare)
        same_duration = same_time_orig[1] - same_time_orig[0]
        print(f'{time.time()-compa_s}\nDone!\n\n')

        print('Processing slicing video 0 (+)')
        video0.slice_video(same_time_orig)
        print('Done!\n\n')

        for i in range(1, len(self.videos_list) + 1):
            video = Video_editor(self.videos_list[i])
            folder_frames = f'{video0.global_path}/{video0.folder_name}'
            print(f'Processing compare frames to {video} (+)')
            time_compare = video.compare_frames_to_video(folder_frames)
            # Now find only one part
            time_compare = time_compare[0][0]
            time_compare = [time_compare, time_compare + same_duration]
            print(f'Done comparing frames to {video}\n\n')

            print(f'Processing slice {video} (+)')
            video.slice_video(time_compare)
            print(f'Done slicing {video}\n\n')
        shutil.rmtree(video0.folder_name)
        print(time.time() - start_time, 'FINISH!!!')
