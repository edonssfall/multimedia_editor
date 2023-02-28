import json

import cv2
import os
import numpy as np


class Video_redactor:
    def __int__(self, name):
        self.name = name

    def open_video(self):
        path = os.getcwd()
        #file = cv2.VideoCapture(f"{os.getcwd()}/{self.name}")
        file = cv2.VideoCapture(self.name)
        file_list = np.array([])
        fps = (file.get(cv2.CAP_PROP_FPS))
        while True:
            ret, frame = file.read()
            print(len(file_list)/720)
            if ret:
                file_list = np.append(file_list, frame)
            else:
                break
        return file_list


video = Video_redactor()
video.name = 'test0.mp4'

video_test = Video_redactor()
video_test.name = 'test0.mp4'
video_array0 = video.open_video()
video_array1 = video_test.open_video()

with open('0.npy', 'wb') as n:
    np.save(n, video_array0)
with open('1.npy', 'wb') as n:
    np.save(n, video_array1)
"""""
with open('0.npy', 'rb') as n:
    video_array0 = np.load(n)
with open('1.npy', 'rb') as n:
    video_array1 = np.load(n)"""

print(video_array0)
