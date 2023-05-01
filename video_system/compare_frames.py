import cv2
import numpy as np


def difference_gray_image(frame_orig, frame_compare):
    """
    Compare two frames with treshold_video in init and mse check with treshold_mse in init
    :param frame_orig: original frame
    :param frame_compare: compare frame
    :return: True or False
    """
    treshold, treshold_mse = 0.65, 40
    gray_orig = cv2.cvtColor(frame_orig, cv2.COLOR_BGR2GRAY)
    gray_compare = cv2.cvtColor(frame_compare, cv2.COLOR_BGR2GRAY)
    difference = cv2.matchTemplate(gray_orig, gray_compare, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(difference)
    if max_val >= treshold:
        return True
    elif max_val < 0:
        return False
    else:
        difference = cv2.absdiff(gray_orig, gray_compare)
        mse = np.mean(difference ** 2)
        if mse <= treshold_mse:
            return True
        else:
            return False


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
