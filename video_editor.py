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

    def __init__(self, name=str(), reserve=2200, threshold_one_color=10, treshold_video=0.7, threshold_mse=40):
        """
        :type reserve: object
        :param
            name: name of video file
            reserve: count of frames that will be compared in first time
            threshold_one_color: value to skip images all one color
            treshold_video: value to compare video from 0 to 1
            threshold_mse: value to compare mse
        """
        self.name = name
        self.folder_name = None
        self.video = None
        self.fps = None
        self.resolution = None
        self.total_frames = None
        self.global_path = None
        self.reserve_orig = reserve
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
        self.video = cv2.VideoCapture(self.name)
        self.folder_name = self.name[:self.name.rfind('.')]
        self.fps = round(self.video.get(cv2.CAP_PROP_FPS))
        self.resolution = round(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = round(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.global_path = os.getcwd()
        self.reserve_compare = self.fps * 2

    def folder_frames(self):
        """
        Make a folder with self.name and choose that folder to save frames there
        """
        folder_path = f'{os.getcwd()}/{self.folder_name}'
        try:
            if not os.path.exists(folder_path):
                os.system(f'mkdir {self.folder_name}')
                os.chdir(folder_path)
            else:
                os.chdir(folder_path)
        except OSError:
            print(f"You don't have permission to change or create")

    def time_compared(self, frames_count_list):
        """
        Take list and make new list with start and end
        with reserve of one sec
        :param frames_count_list: list with same frames compared in counters
        :return: list withs list with seconds [start, end] sec
        """
        reserve = self.reserve_orig
        result = list()
        start, end = frames_count_list[0], int()
        for count in range(1, len(frames_count_list)):
            if frames_count_list[count] - frames_count_list[count - 1] >= reserve:
                reserve = self.reserve_orig
                result.append([start, end])
                start, end = frames_count_list[count], int()
            elif reserve >= 0:
                if frames_count_list[count - 1] + 1 == frames_count_list[count]:
                    end = frames_count_list[count]
                    reserve = self.reserve_orig
                else:
                    reserve -= 1
            else:
                reserve = self.reserve_orig
                result.append([start, end])
                start, end = frames_count_list[count], int()
        result.append(start)
        result.append(end)
        start, end = result[0] / self.fps, result[1] / self.fps
        converted_to_time = [start, end]
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

    def compare_videos(self, video_name=str(), board=int(), boards_compare=list()):
        """
        First compare to find same frames, and make folder with name of second seria
        :param boards_compare: [start, end] of compared video
        :param board: start, auto end in 2 min
        :param video_name: name of compare video
        :return: list of same frames orig video and second of compared [start, end], [start, end] in sec
        """
        video_name = f'{self.global_path}/{video_name}'
        self.folder_frames()
        video_compare = cv2.VideoCapture(video_name)
        same_frames_time_orig, same_frames_time_compare = list(), list()
        frames_counter_orig, frames_counter_compare = int(), int()
        reserve_orig, reserve_compare = self.reserve_orig, self.reserve_compare
        reserve_compare_flag = False
        reopening = False
        with alive_bar(self.reserve_orig) as bar:
            while True:
                ret_orig, frame_orig = self.video.read()
                frames_counter_orig += 1
                # If no more frames or reserved 4 second is done stop function
                if not ret_orig or reserve_orig <= 2:
                    break
                else:
                    # Skip frames if frames counter under the board or frame all is one color
                    if frames_counter_orig - 1 < board or self.check_one_color_frame(frame_orig):
                        continue
                    # If last frame was same, skip opening from the beginning
                    if reopening:
                        # If more than 2 sec is same always turn on reserve_compare
                        if len(same_frames_time_orig) > self.reserve_compare:
                            reserve_compare_flag = True
                        # If was suddenly same frame
                        else:
                            reserve_compare_flag = False
                        reserve_compare = self.reserve_compare
                        boards_compare[0] += 1
                        frames_counter_compare = int()
                        video_compare = cv2.VideoCapture(video_name)
                        reopening = False
                    else:
                        reserve_orig -= 1
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
                                if frames_counter_compare < boards_compare[0] \
                                        or self.check_one_color_frame(frame_compare):
                                    continue
                                else:
                                    # Check that frames same and put flag of same frame and flag to skip reopening
                                    if self.difference_gray_image(frame_orig, frame_compare):
                                        same_frames_time_orig.append(frames_counter_orig - 1)
                                        same_frames_time_compare.append(frames_counter_compare - 1)
                                        boards_compare[0] = frames_counter_compare - 1
                                        reserve_compare = self.reserve_compare
                                        reserve_compare_flag = True
                                        reopening = False
                                        cv2.imwrite(
                                            f'{frames_counter_orig - 1}.jpg',
                                            frame_orig
                                        )
                                        break
                                    # When same frame is open reserve_compare to speed up check
                                    elif reserve_compare_flag:
                                        reserve_compare -= 1
        # Return to folder with videos
        os.chdir('..')
        return self.time_compared(same_frames_time_orig), self.time_compared(same_frames_time_compare)

    def slice_video(self, boards):
        """
        Take [start, end] and cutout this part
        Delete all created files and original video #
        :param boards: [start, end] in sec
        """
        satart = time.time()
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
        # os.remove(txt_file)
        # os.remove(self.name)
        print(time.time() - satart, 'time to slice')

    def compare_frames_to_video(self, folder_frames_path=str(), boards=list()):
        """
        Give path to folder with compared frames
        :param boards: [start, end] in frames
        :param folder_frames_path: path
        :return: timing [start, end] in sec
        """
        os.chdir(folder_frames_path)
        frames_list = sorted(os.listdir())
        frames_counter = int()
        same_frames = list()
        reserve = self.reserve_compare
        reserve_flag = False
        with alive_bar(len(same_frames)) as bar:
            for image in frames_list:
                frame = cv2.imread(image)
                bar()
                while True:
                    ret, frame_compare = self.video.read()
                    frames_counter += 1
                    if len(same_frames) < self.reserve_compare:
                        reserve_flag = False
                        reserve = self.reserve_compare
                    if not ret or reserve <= 0 or frames_counter >= boards[1]:
                        break
                    else:
                        if not frames_counter >= boards[0]:
                            continue
                        else:
                            if self.difference_gray_image(frame, frame_compare):
                                same_frames.append(frames_counter - 1)
                                reserve_flag = True
                                break
                            elif reserve_flag:
                                reserve -= 1
                if reserve <= 0:
                    break
        os.chdir('..')
        return self.time_compared(same_frames)
