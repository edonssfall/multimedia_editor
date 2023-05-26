import math
import cv2
import os
import ffmpeg
import numpy as np
from alive_progress import alive_bar
from video_system import compare_frames


class VideoEditor:
    """
    Class vido file
    Method compare_videos take 2 arguments:
        name of compared vido file, board start time in sec of beginning same part
        return 2 list: same frames of orig video and compared
    Method slice_video take one argument:
        boards is start and end time in sec to cut of from video
        return nothing, just make new video and delete old
    """

    def __init__(self, name: str, threshold=0.7):
        """
        :param name: name of video file
        """
        self.name = name
        self.threshold = threshold
        self.height = None
        self.width = None
        self.time = None
        self.reserve_time_compare = None
        self.short_name = None
        self.format = None
        self.global_path = None
        self.video = None
        self.fps = None
        self.total_frames = None
        self.duration = None
        self.reserve_compare = None
        self.reserve_duration = None
        self.get_video_data()

    def get_video_data(self) -> None:
        """
        Get video-file metadata: open video in OpenCV, edit name(delete part after dot),
        fps, resolution, total frames
        Open file in cv2
        Delete in string name format
        """
        video = cv2.VideoCapture(self.name)
        self.short_name, self.format = os.path.splitext(os.path.basename(self.name))
        self.global_path = self.name[:self.name.find(self.short_name)]
        self.fps = round(video.get(cv2.CAP_PROP_FPS))
        self.height = round(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = round(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.total_frames = round(video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.reserve_compare = self.fps * 2
        self.reserve_time_compare = self.fps * 6
        self.reserve_duration = self.fps * 100

    def time_find_one_par(self, frames_count_list: list) -> list:
        """
        easier time compare to find one paar of time
        take list of frames
        return [start, end]
        """
        count = int()
        start = math.ceil(frames_count_list[0] / self.fps)
        for count in range(len(frames_count_list) - 1):
            if frames_count_list[count + 1] - frames_count_list[count] >= self.reserve_time_compare:
                break
        end = math.floor(frames_count_list[count] / self.fps)
        return [start, end]

    def compare_videos_fast(self, video_name_compare: str, boards_orig: list, boards_compare: list) -> list:
        # TODO: add button to break comparing
        """
        First compare to find same frames
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
                # Stop cycle if frames at board-end
                if not flag_orig or frames_counter_orig >= boards_orig[1]:
                    break
                else:
                    # Skip while frames ist not at board-start
                    if frames_counter_orig < boards_orig[0]:
                        continue
                    # Skip if frame all one color
                    elif compare_frames.check_one_color_frame(frame_orig):
                        bar()
                        continue
                    else:
                        bar()
                        while True:
                            # Reopen compared video, to begin from the start find same frames
                            # Compares board-start + 1
                            # Compare frames counter to zero
                            if reopening:
                                # if it finds less than 1 sec of same frames
                                if len(same_frames) <= self.fps * 1:
                                    same_frames = list()
                                    reserve_compare_flag = False
                                reserve_compare = self.reserve_compare
                                boards_compare[0] += 1
                                frames_counter_compare = -1
                                video_compare = cv2.VideoCapture(video_name_compare)
                                reopening = False
                            ret_compare, frame_compare = video_compare.read()
                            frames_counter_compare += 1
                            # If reserve_compare is empty or frames counter over board or no more frames in the video
                            if not ret_compare or reserve_compare <= 0 or frames_counter_compare >= boards_compare[1]:
                                reopening = True
                                break
                            # When once same part was found, to don't start check from the beginning
                            elif frames_counter_compare < boards_compare[0] or \
                                    compare_frames.check_one_color_frame(frame_compare):
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

    def video_duration_fast(self, video_name_compare: str, boards_orig: list, boards_compare: list) -> list:
        # TODO: add button to break comparing
        """
        Take arguments when know difference at make lists of same frames without skip
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
                        elif compare_frames.difference_gray_image(frame_orig, frame_compare):
                            same_frames_orig.append(frames_counter_orig)
                            same_frames_compare.append(frames_counter_compare)
                            break
                        else:
                            break
        return [same_frames_orig, same_frames_compare]

    def main_compare_func(self, video_name_compare: str, first_sec: int) -> list:
        # TODO: find in first paar time and so on, for next time use only one function
        """
        Make compare of 10sec to find difference in frames
        :param video_name_compare: name of compared video
        :param first_sec: start of same frames in sec
        :return: time of same frames in compared video [start, end] in sec
        """
        first_sec = first_sec * self.fps
        global_video_name_compare = os.path.join(os.getcwd(), video_name_compare)
        boards_orig, boards_compare = [first_sec, first_sec + (self.fps * 10)], [0, self.total_frames / 4]

        # First func to find first 10 sec same frames
        compared = self.compare_videos_fast(global_video_name_compare, boards_orig, boards_compare)

        # If no same or stop button was used
        if len(compared) == 0:
            return [0, 0]

        # Find difference between frames
        differences = [frame[0] - frame[1] for frame in compared]
        difference = int(np.mean(differences))
        # Make boards for second func, to find end of same frames
        same_frames_orig, same_frames_compare = self.video_duration_fast(
            global_video_name_compare,
            [first_sec, first_sec + self.reserve_duration],
            [compared[0][1] + difference, compared[0][1] + self.reserve_duration + difference]
        )

        # Make pars list [start(sec), end(sec)]
        time_orig, time_compared = \
            self.time_find_one_par(same_frames_orig), self.time_find_one_par(same_frames_compare)

        # Write to class time paar
        if self.duration is None or self.duration < time_orig[1] - time_orig[0]:
            self.time = time_orig
            self.duration = time_orig[1] - time_orig[0]
        # If found not enough same frames, just add same time from class to first same frame
        if time_compared[1] - time_compared[0] != self.duration:
            time_compared[1] = time_compared[0] + self.duration
        return time_compared

    def slice_video(self, boards: list) -> None:
        """
        Take [start, end] and cutout this part
        Delete all created files and original video
        :param boards: [start, end] in sec
        """
        duration = self.total_frames * self.fps
        output_file = f"{self.global_path}/{self.short_name}_edonssfall{self.format}"
        if boards[0] == 0:
            (
                ffmpeg
                .input(self.name, ss=boards[1])
                .output(output_file, vcodec='libx264', acodec='aac',
                        t=duration)
                .overwrite_output()
                .run()
            )
        else:
            (
                ffmpeg
                .concat(
                    (ffmpeg.input(self.name, to=boards[0])),
                    (ffmpeg.input(self.name, ss=boards[1]))
                )
                .output(output_file, vcodec='libx264', acodec='aac',
                        t=duration)
                .overwrite_output()
                .run()
            )
