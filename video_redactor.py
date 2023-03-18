import math
from time import time
import cv2
import os


class Video_redactor:
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

    def __init__(self, name=str()):
        """
        :param name: name of video file
        """
        self.name = name
        self.folder_name = None
        self.video = None
        self.fps = None
        self.resolution = None
        self.total_frames = None
        self.get_video_data()

    def get_video_data(self):
        """
        Get videofile metadata: open video in OpenCV, edit name(delete part after dot),
        fps, resolution, total frames
        Open file in cv2
        Delete in string name format
        """
        self.video = cv2.VideoCapture(self.name)
        self.folder_name = self.name[:self.name.rfind('.')]
        self.fps = round(self.video.get(cv2.CAP_PROP_FPS))
        self.resolution = round(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = round(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

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

    def time_compared(self, frames_count_list):
        """
        Take list and make new list with start and end
        with stock of one sec
        :param frames_count_list: list with same frames compared
        :return: list withs list with seconds start and end
        """
        stock = self.fps * 2
        result = list()
        start, end = frames_count_list[0], int()
        for count in range(1, len(frames_count_list)):
            if frames_count_list[count] - frames_count_list[count - 1] >= (self.fps * 2):
                stock = self.fps * 2
                result.append([start, end])
                start, end = frames_count_list[count], int()
            elif stock >= 0:
                if frames_count_list[count - 1] + 1 == frames_count_list[count]:
                    end = frames_count_list[count]
                    stock = self.fps * 2
                else:
                    stock -= 1
            else:
                stock = self.fps * 2
                result.append([start, end])
                start, end = frames_count_list[count], int()
        result.append([start, end])
        converted_to_time = list()
        for seconds in result:
            start, end = seconds[0] / self.fps, seconds[1] / self.fps
            converted_to_time.append([math.ceil(start), math.floor(end)])
        return converted_to_time

    @staticmethod
    def difference_gray_image(frame_orig, frame_compare):
        """
        Compare two frames with treshold 0.99
        :param frame_orig: original frame
        :param frame_compare: compare frame
        :return: True or False
        """
        treshold = 0.9
        gray_orig = cv2.cvtColor(frame_orig, cv2.COLOR_BGR2GRAY)
        gray_compare = cv2.cvtColor(frame_compare, cv2.COLOR_BGR2GRAY)
        difference = cv2.matchTemplate(gray_orig, gray_compare, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(difference)
        if max_val >= treshold:
            return True
        else:
            return False

    def compare_videos(self, video_name, board):
        """
        First compare to find same frames, and make folder with name of second seria
        :param board: start, auto end in 2 min
        :param video_name: name of compare video
        :return: list of same frames orig video and second of compared
        """
        self.folder_frames()
        video_compare = cv2.VideoCapture(self.open_compare_video(video_name))
        same_frames_time_orig, same_frames_time_compare = list(), list()
        frames_counter_orig, frames_counter_compare = int(), int()
        third_part = int(self.total_frames / 3)
        reserve = self.fps * 2
        frames_flag = int()
        reserve_flag = False
        skip_opening = False
        while True:
            ret_orig, frame_orig = self.video.read()
            frames_counter_orig += 1
            if not ret_orig or frames_counter_orig >= board + (board * 2):
                break
            else:
                if frames_counter_orig <= board:
                    continue
                # If last frame was same, skip opening from the beginning
                if not skip_opening:
                    frames_counter_compare = int()
                    video_compare = cv2.VideoCapture(self.open_compare_video(video_name))
                while True:
                    ret_compare, frame_compare = video_compare.read()
                    frames_counter_compare += 1
                    if not ret_compare or frames_counter_compare >= third_part * frames_counter_orig or reserve <= 0:
                        frames_counter_compare = int()
                        reserve = self.fps * 2
                        break
                    else:
                        # When once same part was found, to don't start check from the beginning
                        if frames_counter_compare >= frames_flag:
                            # Check that frames same and put flag of same frame and flag to skip reopening
                            if self.difference_gray_image(frame_orig, frame_compare):
                                same_frames_time_orig.append(frames_counter_orig - 1)
                                same_frames_time_compare.append(frames_counter_compare - 1)
                                frames_flag = frames_counter_compare - 1
                                reserve = self.fps * 2
                                reserve_flag = True
                                skip_opening = True
                                cv2.imwrite(
                                    f'{frames_counter_orig - 1}.jpg',
                                    frame_orig
                                )
                                break
                            elif reserve_flag:
                                reserve -= 1
        os.chdir('..')
        return self.time_compared(same_frames_time_orig), self.time_compared(same_frames_time_compare)

    def slice_video(self, boards):
        """
        Take [start, end] and cutout this part
        Delete all created files and original video #
        :param boards: [start, end]
        """
        duration = self.total_frames * self.fps
        start_video, end_video = f'start_{self.name}', f'end_{self.name}'
        os.system(f"ffmpeg -i {self.name} -ss 0 -c:v libx264 -c:a aac -t {boards[0]} {start_video}")
        os.system(f"ffmpeg -i {self.name} -ss {boards[1]} -c:v libx264 -c:a aac -t {duration} {end_video}")
        txt_file = f'{os.getcwd()}/{self.folder_name}.txt'
        if not os.path.isfile(txt_file):
            os.system(f'touch {txt_file}')
        with open(txt_file, 'r+') as file:
            file.write(f"file 'start_{self.name}'\n"
                       f"file 'end_{self.name}'")
        os.system(f"ffmpeg -f concat -safe 0 -i {txt_file} -c copy {self.folder_name}_edonssfall.mkv")
        os.remove(txt_file)
        os.remove(start_video)
        os.remove(end_video)
        # os.remove(self.name)

    def compare_frames_to_video(self, folder_frames_path):
        """
        Give path to folder with compared frames
        :param folder_frames_path: path
        :return: timing [start, etc]
        """
        os.chdir(folder_frames_path)
        frames_list = sorted(os.listdir())
        frames_counter = int()
        same_frames = list()
        reserve = self.fps * 2
        reserve_flag = False
        for frame in frames_list:
            image = cv2.imread(frame)
            while True:
                ret, frame_compare = self.video.read()
                frames_counter += 1
                if not ret or reserve <= 0:
                    break
                else:
                    if self.difference_gray_image(image, frame_compare):
                        same_frames.append(frames_counter - 1)
                        reserve_flag = True
                    if reserve_flag:
                        reserve -= 1
            if reserve <= 0:
                break
        os.chdir('..')
        return same_frames


start_time = time()
path = '91_Days_[04]_[AniLibria_TV]_[HDTV-Rip_720p].mkv'
video0 = Video_redactor(name=path)
video_c = '91_Days_[05]_[AniLibria_TV]_[HDTV-Rip_720p].mkv'

one_time = [[120, 209], [162, 251]]
# video0.slice_video(one_time[0])

os.chdir(video0.folder_name)
path = os.getcwd()
os.chdir('..')

print(video0.compare_frames_to_video(path))

print(time() - start_time)
