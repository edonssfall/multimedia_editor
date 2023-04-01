import math
import time
import cv2
import os
import numpy as np
from alive_progress import alive_bar


class Video_editor:
    """
    Class vido file
    Method compare_videos take 2 arguments:
        name of compared vido file
        board start time in sec of beginning same part
        return 2 list: same frames of orig video and compared
    Method slice_video take one argument:
        boards is start and end time in sec to cut of from video
        return nothing, just make new video and delete old
    """

    def __init__(self, name=str(), threshold_one_color=10, treshold_video=0.8, threshold_mse=40):
        """
        param:
            name: name of video file
            threshold_one_color: value to skip images all one color
            treshold_video: value to compare video from 0 to 1
            threshold_mse: value to compare mse
        """
        self.time = None
        self.reserve_time = None
        self.name = name
        self.folder_name = None
        self.video = None
        self.fps = None
        self.resolution = None
        self.total_frames = None
        self.global_path = None
        self.duration = None
        self.reserve_compare = None
        self.threshold_one_color = threshold_one_color
        self.treshold = treshold_video
        self.treshold_mse = threshold_mse
        self.get_video_data()

    def get_video_data(self):
        """
        Get video-file metadata: open video in OpenCV, edit name(delete part after dot),
        fps, resolution, total frames
        Open file in cv2
        Delete in string name format
        """
        video = cv2.VideoCapture(self.name)
        self.folder_name = self.name[:self.name.rfind('.')]
        self.fps = round(video.get(cv2.CAP_PROP_FPS))
        self.resolution = round(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = round(video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.global_path = os.getcwd()
        self.reserve_compare = self.fps * 2
        self.reserve_time = self.fps * 6

    def time_compared(self, frames_count_list):
        """
        Take list and make new list with start and end
        with reserve of one sec
        :param frames_count_list: list with same frames compared in counters
        :return: list withs list with seconds [start, end] sec
        """
        reserve = self.reserve_time
        result = list()
        start, end = frames_count_list[0], int()
        for count in range(1, len(frames_count_list) - 1):
            if frames_count_list[count] - frames_count_list[count - 1] >= reserve:
                reserve = self.reserve_time
                result.append(start)
                result.append(end)
                start, end = frames_count_list[count], int()
            elif reserve >= 0:
                if frames_count_list[count - 1] + 1 == frames_count_list[count]:
                    end = frames_count_list[count]
                    reserve = self.reserve_time
                else:
                    reserve -= 1
            else:
                reserve = self.reserve_time
                result.append([start, end])
                start, end = frames_count_list[count], int()
        result.append(start)
        result.append(end)
        start, end = result[0] / self.fps, result[-1] / self.fps
        converted_to_time = [math.ceil(start), math.floor(end)]
        return converted_to_time

    def difference_gray_image(self, frame_orig, frame_compare):
        """
        Compare two frames with treshold_video in init and mse check with treshold_mse in init
        :param frame_orig: original frame
        :param frame_compare: compare frame
        :return: True or False
        """
        gray_orig = cv2.cvtColor(frame_orig, cv2.COLOR_BGR2GRAY)
        gray_compare = cv2.cvtColor(frame_compare, cv2.COLOR_BGR2GRAY)
        difference = cv2.matchTemplate(gray_orig, gray_compare, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(difference)
        if max_val >= self.treshold:
            return True
        elif max_val < 0:
            return False
        else:
            difference = cv2.absdiff(gray_orig, gray_compare)
            mse = np.mean(difference ** 2)
            if mse <= self.treshold_mse:
                return True
            else:
                return False

    @staticmethod
    def check_one_color_frame(frame):
        """
        Take frame and check if is it one color
        :param frame: frame from opencv
        :return: True or False
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean, std = cv2.meanStdDev(gray)
        variance = std[0] ** 2
        if variance < 10:
            return True
        else:
            return False

    def fast_video_compare(self, video_name_compare, first_sec):
        """
        Make compare of 10sec to find difference in frames
        :param video_name_compare: name of compared video
        :param first_sec: start of same frames in sec
        :return: time of same frames in compared video [start, end] in sec
        """
        first_sec = first_sec * self.fps
        global_video_name_compare = f'{self.global_path}/{video_name_compare}'
        treshold_fast = 0.8
        reserved_duration = 2300
        duration = first_sec + (self.fps * 10)
        difference = int()
        list_compare = list()
        boards_orig, boards_compare = [first_sec, duration], [0, self.total_frames / 4]
        compared = self.compare_videos_fast(global_video_name_compare, boards_orig, boards_compare)
        if len(compared) / duration >= treshold_fast:
            for i in compared:
                list_compare.append(i[0] - i[1])
        for i in set(list_compare):
            if list_compare.count(i) / duration >= treshold_fast:
                difference = i
        boards_orig, boards_compare = [first_sec, first_sec + reserved_duration], \
            [compared[0][1] + difference, compared[0][1] + reserved_duration + difference]
        return self.fast_video_duration(global_video_name_compare, boards_orig, boards_compare)

    def compare_videos_fast(self, video_name_compare=str(), boards_orig=list(), boards_compare=list()):
        """
        First compare to find same frames, and make folder with name of second seria
        :param video_name_compare: name of compared video
        :param boards_orig: [start, end] of orig video
        :param boards_compare: [start, end] of compared video
        :return: list of same frames orig video and second of compared [start, end], [start, end] in sec
        """
        video_orig, video_compare = cv2.VideoCapture(self.name), cv2.VideoCapture(video_name_compare)
        same_frames = list()
        frames_counter_orig, frames_counter_compare = -1, -1
        reopening, reserve_compare_flag = False, False
        reserve_compare = self.reserve_compare
        with alive_bar(boards_orig[1]) as bar:
            while True:
                flag_orig, frame_orig = video_orig.read()
                frames_counter_orig += 1
                bar()
                if not flag_orig or frames_counter_orig >= boards_orig[1]:
                    break
                else:
                    if frames_counter_orig < boards_orig[0] or self.check_one_color_frame(frame_orig):
                        continue
                    if reopening:
                        if len(same_frames) <= self.reserve_compare:
                            reserve_compare_flag = False
                            same_frames = list()
                        reserve_compare = self.reserve_compare
                        boards_compare[0] += 1
                        frames_counter_compare = int()
                        video_compare = cv2.VideoCapture(video_name_compare)
                        reopening = False
                    else:
                        while True:
                            ret_compare, frame_compare = video_compare.read()
                            frames_counter_compare += 1
                            # If reserve_compare is empty or frames counter over board or no more frames in the video
                            if not ret_compare or reserve_compare <= 0 or frames_counter_compare >= boards_compare[1]:
                                reopening = True
                                break
                            else:
                                # When once same part was found, to don't start check from the beginning
                                if frames_counter_compare < boards_compare[0]:
                                    continue
                                else:
                                    # Check that frames same and put flag of same frame and flag to skip reopening
                                    if self.difference_gray_image(frame_orig, frame_compare):
                                        same_frames.append([frames_counter_orig, frames_counter_compare])
                                        boards_compare[0] = frames_counter_compare
                                        reserve_compare = self.reserve_compare
                                        reserve_compare_flag = True
                                        reopening = False
                                        break
                                    # When same frame is open reserve_compare to speed up check
                                    elif reserve_compare_flag:
                                        reserve_compare -= 1
        return same_frames

    def fast_video_duration(self, video_name_compare=str(), boards_orig=list(), boards_compare=list()):
        """
        Take arguments when know difference at make list for self and to return
        :param video_name_compare: global name video compare
        :param boards_orig: [start, end] now end 2300 in frames
        :param boards_compare: [start, end] now end - difference +2300  in frames
        :return: time in sec of compared video [start, end]
        """
        video_orig, video_compare = cv2.VideoCapture(self.name), cv2.VideoCapture(video_name_compare)
        frames_counter_orig, frames_counter_compare = -1, -1
        same_frames_orig, same_frames_compare = list(), list()
        with alive_bar(boards_orig[1]) as bar:
            while True:
                ret_orig, frame_orig = video_orig.read()
                frames_counter_orig += 1
                bar()
                if not ret_orig or frames_counter_orig > boards_orig[1]:
                    break
                elif frames_counter_orig < boards_orig[0]:
                    continue
                else:
                    while True:
                        ret_compare, frame_compare = video_compare.read()
                        frames_counter_compare += 1
                        if not ret_compare or frames_counter_compare > boards_compare[1]:
                            break
                        elif frames_counter_compare < boards_compare[0]:
                            continue
                        if self.difference_gray_image(frame_orig, frame_compare):
                            same_frames_orig.append(frames_counter_orig)
                            same_frames_compare.append(frames_counter_compare)
                            break
                        else:
                            break
        if self.duration is None:
            time_orig, time_compare = self.time_compared(same_frames_orig), self.time_compared(same_frames_compare)
            self.time = time_orig
            self.duration = time_orig[1] - time_orig[0]
        else:
            time_compare = self.time_compared(same_frames_compare)
        return time_compare

    def slice_video(self, boards):
        """
        Take [start, end] and cutout this part
        Delete all created files and original video #
        :param boards: [start, end] in sec
        """
        duration = self.total_frames * self.fps
        txt_file = f'{os.getcwd()}/{self.folder_name}.txt'
        if boards[0] == 0:
            os.system(f"ffmpeg -i {self.name} -ss {boards[1]} -c:v libx264 -c:a aac -t "
                      f"{duration} {self.folder_name}_edonssfall.mkv >/dev/null 2>&1")
        else:
            start_video, end_video = f'start_{self.name}', f'end_{self.name}'
            os.system(f"ffmpeg -i {self.name} -ss 0 -c:v libx264 -c:a aac -t {boards[0]} {start_video} "
                      f">/dev/null 2>&1")
            os.system(f"ffmpeg -i {self.name} -ss {boards[1]} -c:v libx264 -c:a aac -t {duration} {end_video} "
                      f">/dev/null 2>&1")
            if not os.path.isfile(txt_file):
                os.system(f'touch {txt_file}')
            with open(txt_file, 'r+') as file:
                file.write(f"file 'start_{self.name}'\n"
                           f"file 'end_{self.name}'")
            os.system(f"ffmpeg -f concat -safe 0 -i {txt_file} -c copy {self.folder_name}_edonssfall.mkv "
                      f">/dev/null 2>&1")
            os.remove(start_video)
            os.remove(end_video)
            os.remove(txt_file)
        os.remove(self.name)
