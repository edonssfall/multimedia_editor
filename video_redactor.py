import cv2
import os

class Video_redactor:

    def __int__(self, name=str):
        self.name = name

    def open_video(self):
        path = os.getcwd()
        video = cv2.capture