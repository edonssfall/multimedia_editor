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
        Open file in cv2
        Delete in string name format
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
        Make a folder with self.name and choose that folder to save frames there
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

    def image_name(self, time_list):
        name = f'{self.name}'\
               f'_{str(time_list[0]).zfill(2)}'\
               f':{str(time_list[1]).zfill(2)}'\
               f':{str(time_list[2]).zfill(2)}'\
               f':{str(time_list[3])[2:].zfill(3)}.jpg'
        return name

    def split_video_to_frames(self):
        """
        Split videofile to frames, save and call them as (self.name_HH:MM:SS:MSS.jpg)
        """
        self.folder_frames()
        frames_counter = 1
        time_list = [0, 0, 0, 0]
        while True:
            ret, frame = self.video.read()
            if ret:
                time_list = self.count_time(frames_counter, time_list)
                cv2.imwrite(
                    self.image_name(time_list),
                    frame
                )
            else:
                break
            frames_counter += 1

    @staticmethod
    def check_one_color(frame):
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_color_per_row = np.average(gray_image, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        if avg_color > 200:
            return False
        else:
            return True

    @staticmethod
    def open_compare_video(video_name):
        global_path_to_vide = os.getcwd()
        global_path_to_vide = f"{global_path_to_vide[:global_path_to_vide.rfind('/')]}/{video_name}"
        return global_path_to_vide

    @staticmethod
    def find_index(list1, list2):
        for i in range(len(list1)):
            if list1[i] == list2:
                return i

    def find_timecode_same_frames(self, time_list):
        timing_list = []
        end_same = []
        while True:
            start_same = time_list[0]
            for i in range(1, len(time_list)):
                compare_time_list = self.count_time(i, time_list[i-1])
                if time_list[i] == compare_time_list:
                    end_same = compare_time_list
            else:
                timing_list.append([start_same, end_same])
                time_list = time_list[self.find_index(time_list, end_same):]
                end_same = []
                continue

    def compare_video(self, video_name):
        """
        First compare to find same frames
        :param video_name: video name to find all same
        :return: list of same frames
        """
        self.folder_frames()
        same_frames_time = []
        time_list_orig = [0, 0, 0, 0]
        frames_counter_orig = 1
        while True:
            ret_orig, frame_orig = self.video.read()
            time_list_orig = self.count_time(frames_counter_orig, time_list_orig)
            if ret_orig:
                video_compare = cv2.VideoCapture(self.open_compare_video(video_name))
                while True:
                    ret_compare, frame_compare = video_compare.read()
                    if ret_compare:
                        difference = cv2.absdiff(frame_orig, frame_compare)
                        if np.nonzero(difference):
                            cv2.imwrite(
                                self.image_name(time_list_orig),
                                frame_orig
                            )
                            same_frames_time.append(time_list_orig)
                            break
                    else:
                        break
            else:
                break
            frames_counter_orig += 1
        return same_frames_time


start = time()
path = 'test.mp4'
video = Video_redactor(name=path)

video_c = 'test.mp4'
video.find_timecode_same_frames([[0, 4, 10, 0],
                                [0, 4, 10, 0.033],
                                [0, 4, 10, 0.066],
                                [0, 4, 10, 0.099],
                                [0, 4, 10, 0.132],
                                [0, 4, 10, 0.165],
                                [0, 4, 10, 0.198],
                                [0, 4, 10, 0.231],
                                [0, 4, 10, 0.264],
                                [0, 4, 10, 0.297],
                                [0, 4, 10, 0.33],
                                [0, 4, 10, 0.363],
                                [0, 4, 10, 0.396],
                                [0, 4, 10, 0.429],
                                [0, 4, 10, 0.462],
                                [0, 4, 10, 0.495],
                                [0, 4, 10, 0.528],
                        [0, 4, 10, 0.561]])
end: float = time() - start
print(end)
