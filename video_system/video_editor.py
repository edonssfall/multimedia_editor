import math
import cv2
import os
import keyboard
from alive_progress import alive_bar
from video_system import compare_frames


class VideoEditor:
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
    def __init__(self, name=str(), threshold_one_color=10, threshold=0.7):
        """
        :param name: name of video file
        :param threshold_one_color: value to skip images all one color(standard=10)
        """
        self.name = name
        self.resolution = None
        self.time = None
        self.reserve_time_compare = None
        self.short_name = None
        self.video = None
        self.fps = None
        self.total_frames = None
        self.duration = None
        self.reserve_compare = None
        self.reserve_duration = None
        self.treshold = threshold
        self.threshold_one_color = threshold_one_color
        self.get_video_data()

    def get_video_data(self):
        """
        Get video-file metadata: open video in OpenCV, edit name(delete part after dot),
        fps, resolution, total frames
        Open file in cv2
        Delete in string name format
        """
        video = cv2.VideoCapture(self.name)
        self.short_name = os.path.splitext(os.path.basename(self.name))[0]
        self.fps = round(video.get(cv2.CAP_PROP_FPS))
        self.resolution = round(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = round(video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.reserve_compare = self.fps * 2
        self.reserve_time_compare = self.fps * 5
        self.reserve_duration = self.fps * 100

    def time_compare(self, frames_count_list):
        """
        Take list and make new list with start and end
        with reserve of one sec
        :param frames_count_list: list with same frames compared in counters
        :return: list withs list with seconds [start, end] sec
        """
        reserve = self.reserve_time_compare
        result = list()
        start, end = frames_count_list[0], int()
        for count in range(1, len(frames_count_list) - 1):
            if frames_count_list[count] - frames_count_list[count - 1] >= self.reserve_time_compare:
                reserve = self.reserve_time_compare
                result.append(start)
                result.append(end)
                start, end = frames_count_list[count], int()
            elif reserve >= 0:
                if frames_count_list[count - 1] + 1 == frames_count_list[count]:
                    end = frames_count_list[count]
                    reserve = self.reserve_time_compare
                else:
                    reserve -= 1
            else:
                reserve = self.reserve_time_compare
                result.append([start, end])
                start, end = frames_count_list[count], int()
        result.append(start)
        result.append(end)
        start, end = result[0] / self.fps, result[-1] / self.fps
        converted_to_time = [math.ceil(start), math.floor(end)]
        return converted_to_time

    def time_find_one_paar(self, frames_count_list):
        """
        easier time compare to find one paar of time
        take list of frames
        return [start, end]
        """
        start = math.ceil(frames_count_list[0] / self.fps)
        for count in range(len(frames_count_list) - 1):
            if frames_count_list[count + 1] - frames_count_list[count] >= self.reserve_time_compare:
                break
        end = math.floor(frames_count_list[count] / self.fps)
        return [start, end]

    def compare_videos_fast(self, video_name_compare, boards_orig, boards_compare):
        # TODO: add button to break comparing
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
        with alive_bar(boards_orig[1] - boards_orig[0]) as bar:
            while True:
                flag_orig, frame_orig = video_orig.read()
                frames_counter_orig += 1
                if not flag_orig or frames_counter_orig >= boards_orig[1]:
                    break
                else:
                    if frames_counter_orig < boards_orig[0]:
                        continue
                    if compare_frames.check_one_color_frame(frame_orig):
                        bar()
                        continue
                    if reopening:
                        if len(same_frames) <= self.fps * 1:
                            reserve_compare_flag = False
                        reserve_compare = self.reserve_compare
                        boards_compare[0] += 1
                        frames_counter_compare = int()
                        video_compare = cv2.VideoCapture(video_name_compare)
                        reopening = False
                    else:
                        bar()
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
                                    if compare_frames.difference_gray_image(frame_orig, frame_compare):
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

    def video_duration_fast(self, video_name_compare, boards_orig, boards_compare):
        # TODO: add button to break comparing
        """
        Take arguments when know difference at make lists of same frames
        :param video_name_compare: global name video compare
        :param boards_orig: [start, end] now end 2300 in frames
        :param boards_compare: [start, end] now end - difference +2300  in frames
        :return: time in sec of compared video [start, end]
        """
        video_orig, video_compare = cv2.VideoCapture(self.name), cv2.VideoCapture(video_name_compare)
        frames_counter_orig, frames_counter_compare = -1, -1
        same_frames_orig, same_frames_compare = list(), list()
        with alive_bar(boards_orig[1] - boards_orig[0]) as bar:
            while True:
                ret_orig, frame_orig = video_orig.read()
                frames_counter_orig += 1
                if not ret_orig or frames_counter_orig > boards_orig[1]:
                    break
                elif frames_counter_orig < boards_orig[0]:
                    continue
                else:
                    bar()
                    while True:
                        ret_compare, frame_compare = video_compare.read()
                        frames_counter_compare += 1
                        if not ret_compare or frames_counter_compare > boards_compare[1]:
                            break
                        elif frames_counter_compare < boards_compare[0]:
                            continue
                        if compare_frames.difference_gray_image(frame_orig, frame_compare):
                            same_frames_orig.append(frames_counter_orig)
                            same_frames_compare.append(frames_counter_compare)
                            break
                        else:
                            break
        time_orig, time_compared = \
            self.time_find_one_paar(same_frames_orig), self.time_find_one_paar(same_frames_compare)
        if self.duration is None or self.duration < time_orig[1] - time_orig[0]:
            self.time = time_orig
            self.duration = time_orig[1] - time_orig[0]
        if time_compared[1] - time_compared[0] != self.duration:
            time_compared[1] = time_compared[0] + self.duration
        return time_compared

    def main_compare_func(self, video_name_compare, first_sec):
        """
        Make compare of 10sec to find difference in frames
        :param video_name_compare: name of compared video
        :param first_sec: start of same frames in sec
        :return: time of same frames in compared video [start, end] in sec
        """
        first_sec = first_sec * self.fps
        # here change to universal
        global_video_name_compare = os.path.join(os.getcwd(), video_name_compare)
        duration = first_sec + (self.fps * 10)
        difference = int()
        list_compare = list()
        boards_orig, boards_compare = [first_sec, duration], [0, self.total_frames / 4]
        compared = self.compare_videos_fast(global_video_name_compare, boards_orig, boards_compare)
        if len(compared) == 0:
            return [0, 0]
        if len(compared) / duration >= self.treshold:
            for i in compared:
                list_compare.append(i[0] - i[1])
        for i in set(list_compare):
            if list_compare.count(i) / duration >= self.treshold:
                difference = i
        boards_orig, boards_compare = [first_sec, first_sec + self.reserve_duration], \
            [compared[0][1] + difference, compared[0][1] + self.reserve_duration + difference]
        return self.video_duration_fast(global_video_name_compare, boards_orig, boards_compare)

    def slice_video(self, boards):
        """
        Take [start, end] and cutout this part
        Delete all created files and original video
        :param boards: [start, end] in sec
        """
        duration = self.total_frames * self.fps
        txt_file = f'{self.short_name}.txt'
        if boards[0] == 0:
            os.system(f"ffmpeg -i {self.name} -ss {boards[1]} -c:v libx264 -c:a aac -t "
                      f"{duration} {self.short_name}_edonssfall.mkv >/dev/null 2>&1")
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
            os.system(f"ffmpeg -f concat -safe 0 -i {txt_file} -c copy {self.short_name}_edonssfall.mkv "
                      f">/dev/null 2>&1")
            os.remove(start_video)
            os.remove(end_video)
            os.remove(txt_file)
        os.remove(self.name)
