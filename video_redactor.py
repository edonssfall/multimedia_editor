import os
from time import time
import cv2
from multiprocessing import Pool


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
        self.total_frames = None
        self.get_video_data()

    def get_video_data(self):
        """
        Get videofile metadata: fps, fpms, resolution
        Open file in cv2
        Delete in string name format
        """
        self.video = cv2.VideoCapture(self.name)
        self.name = self.name[:self.name.rfind('.')]
        self.fps = round(self.video.get(cv2.CAP_PROP_FPS))
        self.fpms = round(1 / self.fps, 3)
        self.resolution = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

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
    def open_compare_video(video_name):
        """
        Open vidio for first compare by global path
        :param video_name: video name
        :return:
        """
        global_path_to_video = os.getcwd()
        global_path_to_video = f"{global_path_to_video[:global_path_to_video.rfind('/')]}/{video_name}"
        return global_path_to_video

    def frame_count_to_time(self, frame):
        hours, minutes = int(), int()
        seconds = frame / self.fps
        print(seconds, frame, self.fps)
        minutes, seconds = self.equal_to_60(minutes, seconds)
        hours, minutes = self.equal_to_60(hours, minutes)
        frame_time = [hours, minutes, round(seconds, 3)]
        print(frame_time, frame)
        return frame_time

    @staticmethod
    def equal_to_60(number1, number2):
        if number2 >= 60:
            number1 = int(number2 // 60)
            number2 = number2 - (number1 * 60)
        return number1, number2

    def find_timecode_same_frames(self, time_list):
        """
        Cut all timings, to find granicy
        :param time_list: list of timings of same frames
        :return:
        """
        timing_list, end_same = list(), list()
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
        timing_start, timing_end = list(), list()
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

    @staticmethod
    def difference_gray_image(frame_orig, frame_compare):
        """
        Compare two frames with treshold 0.99
        :param frame_orig: original frame
        :param frame_compare: compare frame
        :return: True or False
        """
        treshold = 0.2
        gray_orig = cv2.cvtColor(frame_orig, cv2.COLOR_BGR2GRAY)
        gray_compare = cv2.cvtColor(frame_compare, cv2.COLOR_BGR2GRAY)
        difference = cv2.matchTemplate(gray_orig, gray_compare, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(difference)
        if max_val >= treshold:
            return True
        else:
            return False

    def compare_videos(self, video_name, time_boards):
        """
        First compare to find same frames, and make folder with name of second seria
        :param time_boards: list start and end of orig and compare
        :param video_name: name of compare video
        :return: list of same frames orig video and second of compared
        """
        self.folder_frames()
        video_compare = cv2.VideoCapture(self.open_compare_video(video_name))
        same_frames_time_orig, same_frames_time_compare = list(), list()
        frames_counter_orig, frames_counter_compare = -1, -1
        frames_flag = int()
        skip_opening = False

        while True:
            ret_orig, frame_orig = self.video.read()
            if ret_orig:
                frames_counter_orig += 1
                # Break when time same to end time
                if frames_counter_orig >= time_boards[1]:
                    break
                # Skip while time be at start mark
                elif frames_counter_orig >= time_boards[0]:
                    # If last frame was same, skip opening from the beginning
                    if not skip_opening:
                        frames_counter_compare = int()
                        video_compare = cv2.VideoCapture(self.open_compare_video(video_name))
                    while True:
                        ret_compare, frame_compare = video_compare.read()
                        # While video opening
                        if ret_compare:
                            frames_counter_compare += 1
                            # Break when time same to end time
                            if frames_counter_compare >= time_boards[3]:
                                break
                            # Skip while time be at start mark
                            if frames_counter_compare >= time_boards[2]:
                                # When once same part was found, to don't start check from the beginning
                                if frames_counter_compare >= frames_flag:
                                    # Check that frames same and put flag of same frame and flag to skip reopening
                                    if self.difference_gray_image(frame_orig, frame_compare):
                                        frame_name = self.frame_count_to_time(frames_counter_orig)
                                        same_frames_time_orig.append(frames_counter_orig)
                                        same_frames_time_compare.append(frames_counter_compare)
                                        frames_flag = frames_counter_compare
                                        skip_opening = True
                                        cv2.imwrite(
                                            f'{str(frame_name[0]).zfill(2)}:'
                                            f'{str(frame_name[1]).zfill(2)}:'
                                            f'{str(frame_name[2]).zfill(5)}'
                                            f'.jpg',
                                            frame_orig
                                        )
                                        break
                                else:
                                    skip_opening = False
                        else:
                            break
            else:
                break
        print(same_frames_time_orig, same_frames_time_compare)

    def multiprocessing_cpu(self, cores_count, video_name):
        """
        Main process to multicompare video using CPU
        :param cores_count: count cores
        :param video_name: name of compare video
        :return: time to slice both videos
        """
        orig_same_list, compare_same_list = list(), list()
        video = cv2.VideoCapture(video_name)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        big_part_orig = (self.total_frames / self.fps) / 3
        big_part_compare = (total_frames / fps) / 3
        small_part_orig = big_part_orig / cores_count
        for parts in range(3):
            start_compare = (parts * big_part_compare)
            end_compare = start_compare + big_part_compare
            for piece in range(cores_count):
                start_orig = (parts * big_part_orig) + (piece * small_part_orig)
                end_orig = start_orig + small_part_orig
                boards_list = [start_orig, end_orig, start_compare, end_compare]
        print(orig_same_list, compare_same_list, sep='\n')

    def compare_frames_Pool(self, frame_orig, frame_compare):
        threshold = 0.95
        gray_orig = cv2.cvtColor(frame_orig, cv2.COLOR_BGR2GRAY)
        gray_compare = cv2.cvtColor(frame_compare, cv2.COLOR_BGR2GRAY)
        h, w = gray_orig.shape
        result = cv2.matchTemplate(gray_orig, gray_compare, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            return True
        else:
            return False

    def comapre_videos_Pool(self, video_name, boards):
        self.folder_frames()
        video_compare = cv2.VideoCapture(self.open_compare_video(video_name))
        same_frames_orig, same_frames_compare = list(), list()
        frames_counter_orig, frames_counter_compare = int(), int()
        frames_flag = 1
        skip_opening = False
        with Pool() as pool:
            while True:
                ret_orig, frame_orig = self.video.read()
                if ret_orig:
                    if frames_counter_orig >= boards[0]:
                        break
                    elif frames_counter_orig >= boards[1]:
                        if not skip_opening:
                            frames_counter_compare = int()
                            video_compare = cv2.VideoCapture(self.open_compare_video(video_name))
                        while True:
                            ret_compare, frame_compare = video_compare.read()
                            if ret_compare:
                                if frames_counter_compare >= boards[2]:
                                    break
                                elif frames_counter_compare >= boards[3] or frames_counter_compare <= frames_flag:
                                    result = pool.apply_async(self.compare_frames_Pool, (frame_orig, frame_compare))
                                    if result:
                                        cv2.imwrite(frames_counter_orig, frame_orig)
                                        same_frames_orig.append(frames_counter_orig)
                                        same_frames_compare.append(frames_counter_compare)
                                        frames_flag = frames_counter_compare
                                frames_counter_compare += 1
                            else:
                                break
                    frames_counter_orig += 1
                else:
                    break
            print(same_frames_orig, same_frames_compare)


start_time = time()
path = '91_Days_[04]_[AniLibria_TV]_[HDTV-Rip_720p].mkv'
video0 = Video_redactor(name=path)
video_c = '91_Days_[05]_[AniLibria_TV]_[HDTV-Rip_720p].mkv'

time_listt = [120, 122, 2 * 60, 4 * 60]
boards = [2880, 2885, 2880, 5760]

video0.compare_videos(video_c, boards)

print(time() - start_time)
