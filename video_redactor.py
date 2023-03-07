import math
import ffmpeg
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
        folder_path = f'{os.getcwd()}/{self.name}'
        try:
            if not os.path.exists(folder_path):
                os.system(f'mkdir {self.name}')
                os.chdir(folder_path)
            else:
                os.chdir(folder_path)
        except OSError:
            print(f"You don't have permission to change or create")

    def image_name(self, time_list):
        """
        Make name for image
        :param time_list: list with time code of frame
        :return: self.name_HH:MM:SS:MSS
        """
        name = f'{self.name}'\
               f'_{str(time_list[0]).zfill(2)}'\
               f':{str(time_list[1]).zfill(2)}'\
               f':{str(time_list[2]).zfill(2)}'\
               f':{str(time_list[3])[2:].zfill(3)}.jpg'
        return name

    @staticmethod
    def timing_name(start, end):
        """
        return start end round milliseconds
        :param start:
        :param end:
        :return:
        """
        timing_start = f'{str(start[0]).zfill(2)}.' \
                       f'{str(start[1]).zfill(2)}.' \
                       f'{str(start[2]).zfill(2)}'
        timing_end = f'{str(end[0]).zfill(2)}.' \
                     f'{str(end[1]).zfill(2)}.' \
                     f'{str(end[2]).zfill(2)}'
        return timing_start, timing_end

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
                frames_counter += 1
                cv2.imwrite(
                    self.image_name(time_list),
                    frame
                )
            else:
                break

    @staticmethod
    def difference_gray_image(frame_orig, frame_compare):
        treshold = 0.99
        gray_orig = cv2.cvtColor(frame_orig, cv2.COLOR_BGR2GRAY)
        gray_compare = cv2.cvtColor(frame_compare, cv2.COLOR_BGR2GRAY)
        difference = cv2.matchTemplate(gray_orig, gray_compare, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(difference)
        if max_val >= treshold:
            return True
        else:
            return False

    @staticmethod
    def open_compare_video(video_name):
        """
        Open vidio for first compare by global path
        :param video_name: video name
        :return:
        """
        global_path_to_vide = os.getcwd()
        global_path_to_vide = f"{global_path_to_vide[:global_path_to_vide.rfind('/')]}/{video_name}"
        return global_path_to_vide

    @staticmethod
    def sum_time(time_list):
        time_sum = time_list[0] * 180 + time_list[1] * 60 + time_list[2] + time_list[3]
        return time_sum

    def find_timecode_same_frames(self, time_list):
        """
        Cut all timings, to find granicy
        :param time_list: list of timings of same frames
        :return:
        """
        timing_list = []
        end_same = []
        start_same = time_list[0]
        for i in range(1, len(time_list)):
            compare_time_list = self.count_time(1, time_list[i-1])
            if time_list[i] == compare_time_list:
                end_same = compare_time_list
                if end_same == time_list[-1]:
                    timing_list.append([start_same, end_same])
            else:
                timing_list.append([start_same, end_same])
                start_same = time_list[i]
                end_same = []
        self.encode_timings(timing_list)

    def encode_timings(self, timings_list):
        """
        Encoding time list for moviepy to cut parts
        :param timings_list:
        :return:
        """
        for i in timings_list:
            start = i[0]
            end = i[1]
            if end[2] - start[2] >= 9:
                if start[4] != 0:
                    start[3] = start[3] + 1
                if end[4] != 0:
                    end[3] = end[3] - 1
            timing_start, timing_end = self.timing_name(start, end)
        print(timing_start, timing_end)

    def compare_video(self, video_name, time_orig, time_compare):
        """
        First compare to find same frames, and make folder with name of second seria
        :param time_compare: list minute and second start and end at original video
        :param time_orig: list minute and second start and end at video compare
        :param video_name: name of compare video
        :return: list of same frames orig video and second of compared
        """
        self.folder_frames()
        start_time_orig, end_time_orig = time_orig[0], time_orig[1]
        start_time_compare, end_time_compare = time_compare[0], time_compare[1]
        video_compare = cv2.VideoCapture(self.open_compare_video(video_name))
        same_frames_time_orig, same_frames_time_compare = [], []
        time_list_orig, time_list_compare = [0, 0, 0, 0], [0, 0, 0, 0]
        frames_counter_orig, frames_counter_compare = 1, 1
        frames_flag = 1
        skip_opening = False

        while True:
            ret_orig, frame_orig = self.video.read()
            if ret_orig:
                time_list_orig = self.count_time(frames_counter_orig, time_list_orig)
                frames_counter_orig += 1
                # Break when time same to end time
                if self.sum_time(time_list_orig) >= end_time_orig:
                    break
                # Skip while time be at start mark
                if self.sum_time(time_list_orig) >= start_time_orig:
                    print(time_list_orig)
                    # If last frame was same, skip opening from the beginning
                    if not skip_opening:
                        time_list_compare = [0, 0, 0, 0]
                        frames_counter_compare = 0
                        video_compare = cv2.VideoCapture(self.open_compare_video(video_name))
                    while True:
                        ret_compare, frame_compare = video_compare.read()
                        # While video opening
                        if ret_compare:
                            frames_counter_compare += 1
                            time_list_compare = self.count_time(frames_counter_compare, time_list_compare)
                            # Break when time same to end time
                            if self.sum_time(time_list_compare) >= end_time_compare:
                                break
                            # Skip while time be at start mark
                            if self.sum_time(time_list_compare) >= start_time_compare:
                                #print(time_list_compare)
                                # When once same part was found, to don't start check from the beginning
                                if frames_counter_compare >= frames_flag:
                                    # Check that frames same and put flag of same frame and flag to skip reopening
                                    if self.difference_gray_image(frame_orig, frame_compare):
                                        cv2.imwrite(
                                            self.image_name(time_list_orig),
                                            frame_orig
                                        )
                                        print('wihu')
                                        same_frames_time_orig.append(time_list_orig)
                                        same_frames_time_compare.append(time_list_compare)
                                        frames_flag = frames_counter_compare
                                        skip_opening = True
                                        break
                                    else:
                                        skip_opening = False
                                        continue
                                else:
                                    continue
                            else:
                                continue
                        else:
                            break
                else:
                    continue
            else:
                break
        self.find_timecode_same_frames(same_frames_time_orig)
        self.find_timecode_same_frames(same_frames_time_compare)


start_time = time()


path = '91_Days_[04]_[AniLibria_TV]_[HDTV-Rip_720p].mkv'
#path = 'test.mp4'
video = Video_redactor(name=path)

video_c = '91_Days_[05]_[AniLibria_TV]_[HDTV-Rip_720p].mkv'
#video_c = 'test.mp4'

orig_time_list = [120, 4 * 60]
#compare_time_list = [120, 4 * 60]
compare_time_list = [2 * 60 + 35, 3 * 60]
#orig_time_list = [0, 10]
#compare_time_list = [0, 10]

video.compare_video(video_c, orig_time_list, compare_time_list)

print(time() - start_time)
