import os
from time import time
import cv2
import numpy as np


class Video_redactor:

    def __init__(self, name=str):
        """
        :param name: name of video file
        """
        self.name = name
        self.video = None
        self.fps = None
        self.fpms = None
        self.resolution = None
        self.get_video_data()

    def get_video_data(self):
        """
        Get videofile metadata: fps, fpms, resolution
        and open file in cv2
        """
        self.video = cv2.VideoCapture(self.name)
        self.name = self.name[:self.name.rfind('.')]
        self.fps = round(self.video.get(cv2.CAP_PROP_FPS), 0)
        self.fpms = round(1 / self.fps, 3)
        self.resolution = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @staticmethod
    def equal_to_60(num1, num2):
        """
        Check milliseconds or seconds, or minutes for +1 second, minute or hour
        """
        if num1 >= 60:
            num1 = 0
            num2 += 1
        return num1, num2

    def count_time(self, frame, time_list):
        """
        Video duration 24:30 round 8 minutes with cpu
        Split video file to frames in folder with name of videofile
        """
        hours, minutes, seconds, milliseconds = time_list[0], time_list[1], time_list[2], time_list[3]
        milliseconds += self.fpms
        if frame % self.fps == 0:
            milliseconds = 0
            seconds += 1
        seconds, minutes = self.equal_to_60(seconds, minutes)
        minutes, hours = self.equal_to_60(minutes, hours)
        time_list = [int(hours), int(minutes), int(seconds), round(milliseconds, 3)]
        return time_list

    def folder_frames(self):
        """
        Make a folder with self.name and choose that folder to fold frames there
        """
        folder_path = os.getcwd()
        try:
            if not os.path.exists(self.name):
                os.system(f'mkdir {self.name}')
                os.chdir(f'{folder_path}/{self.name}')
            else:
                os.chdir(f'{folder_path}/{self.name}')
        except OSError:
            print(f"You don't have permission to change or create")

    def split_video_to_frames(self):
        """
        Split videofile to frames and call them in (self.name_HH:MM:SS:MSS)
        """
        self.folder_frames()
        frames_counter = 1
        time_list = [0, 0, 0, 0]
        while True:
            ret, frame = self.video.read()
            if ret:
                time_list = self.count_time(frames_counter, time_list)
                cv2.imwrite(
                    f'{self.name}'
                    f'_{str(time_list[0]).zfill(2)}'
                    f':{str(time_list[1]).zfill(2)}'
                    f':{str(time_list[2]).zfill(2)}'
                    f':{str(time_list[3])[2:].zfill(3)}.jpg',
                    frame
                )
            else:
                break
            frames_counter += 1


start = time()
path = '91_Days_[05]_[AniLibria_TV]_[HDTV-Rip_720p].mkv'
video = Video_redactor(name=path)

end: float = time() - start
print(end)
