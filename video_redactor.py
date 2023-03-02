import os
from time import time
import cv2
import numpy as np


def get_video_data(file_name):
    """
    Get videofile metadata: fps, fpms, resolution
    and open file in cv2
    :param file_name: name of file
    :return: list with metadata
    """
    video_file = cv2.VideoCapture(file_name)
    name = file_name[:file_name.rfind(".")]
    fps = video_file.get(cv2.CAP_PROP_FPS)
    fpms = 1 / fps
    resolution = int(video_file.get(cv2.CAP_PROP_FRAME_HEIGHT))
    meta_data = np.array([video_file, name, round(fps, 0), round(fpms, 3), resolution])
    return meta_data


def equal_or_60(num1, num2):
    """
    Check milliseconds or seconds or minutes for +1 second minute or hour
    """
    if num1 >= 60:
        num1 = 0
        num2 += 1
    return num1, num2


class Video_redactor:

    def __init__(self, video_cv2, name=str, fps=int, fpms=float, resolution=int):
        """
        :param video_cv2: open file in cv2
        :param name: name of folder
        :param fps: frames per second
        :param fpms: milliseconds for one frame
        :param resolution: quality resolution
        """
        self.name = name
        self.video = video_cv2
        self.fps = fps
        self.fpms = fpms
        self.resolution = resolution

    def count_time(self, frame, time_list):
        """
        Video duration 24:30 round 8 minutes
        Split video file to frames in folder with name of videofile
        """
        h, m, s, ms = time_list[0], time_list[1], time_list[2], time_list[3]
        ms += self.fpms
        if frame % self.fps == 0:
            ms = 0
            s += 1
        s, m = equal_or_60(s, m)
        m, h = equal_or_60(m, h)
        time_list = [int(h), int(m), int(s), round(ms, 3)]
        return time_list

    def folder_frames(self):
        """
        Make a folder with self.name and choose that folder to fold frames there
        """
        folder_path = os.getcwd()
        try:
            if os.path.exists(self.name):
                os.chdir(f'{folder_path}/{self.name}')
            else:
                os.system(f'mkdir {self.name}')
                os.chdir(f'{folder_path}/{self.name}')
        except OSError:
            print(f"You don't have permission to change or create")

    def split_video_to_frames(self):
        """
        Split videofile to frames and call them in (self.name_HH:MM:SS:MSS)
        """
        self.folder_frames()
        frames = 1
        time_list = [0, 0, 0, 0]
        while True:
            ret, frame = self.video.read()
            if ret:
                time_list = self.count_time(frames, time_list)
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
            frames += 1


start = time()
path = '91_Days_[05]_[AniLibria_TV]_[HDTV-Rip_720p].mkv'
video_data = get_video_data(path)

video = Video_redactor(
    video_cv2=video_data[0],
    name=video_data[1],
    fps=video_data[2],
    fpms=video_data[3],
    resolution=video_data[4]
)

video.split_video_to_frames()
end = time() - start
print(end)
