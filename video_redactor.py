from moviepy.editor import *
import cv2
import os


class Video_redactor:
    def __int__(self, name):
        self.name = name

    def open_video(self):
        path = os.getcwd()
        print(self.name)
        file = cv2.VideoCapture(self.name)
        print(file)


video = Video_redactor()
video.name = 'test.mp4'
video.open_video()
