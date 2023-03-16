import math
import os
from time import time
import cv2


class Video_redactor:

    def __init__(self, name=str()):
        """
        :param name: name of video file
        """
        self.name = name
        self.video = None
        self.fps = None
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
        self.resolution = round(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = round(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

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
        stock = self.fps
        result = list()
        start, end = frames_count_list[0], int()
        for count in range(1, len(frames_count_list)):
            if frames_count_list[count] - frames_count_list[count - 1] >= self.fps:
                stock = self.fps
                result.append([start, end])
                start, end = frames_count_list[count], int()
            elif stock >= 0:
                if frames_count_list[count - 1] + 1 == frames_count_list[count]:
                    end = frames_count_list[count]
                    stock = self.fps
                else:
                    stock -= 1
            else:
                stock = self.fps
                result.append([start, end])
                start, end = frames_count_list[count], int()
        result.append([start, end])
        converted_to_time = list()
        for seconds in result:
            start, end = self.frame_count_to_time(seconds[0]), self.frame_count_to_time(seconds[1])
            converted_to_time.append([math.ceil(start), math.floor(end)])
        return converted_to_time

    def frame_count_to_time(self, frame):
        seconds = frame / self.fps
        return seconds

    @staticmethod
    def difference_gray_image(frame_orig, frame_compare):
        """
        Compare two frames with treshold 0.99
        :param frame_orig: original frame
        :param frame_compare: compare frame
        :return: True or False
        """
        treshold = 0.99
        gray_orig = cv2.cvtColor(frame_orig, cv2.COLOR_BGR2GRAY)
        gray_compare = cv2.cvtColor(frame_compare, cv2.COLOR_BGR2GRAY)
        difference = cv2.matchTemplate(gray_orig, gray_compare, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(difference)
        if max_val >= treshold:
            return True
        else:
            return False

    def compare_videos(self, video_name):
        """
        First compare to find same frames, and make folder with name of second seria
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
                print(frames_counter_orig)
                # need to add skip empty frames
                # If last frame was same, skip opening from the beginning
                if not skip_opening:
                    frames_counter_compare = -1
                    video_compare = cv2.VideoCapture(self.open_compare_video(video_name))
                while True:
                    ret_compare, frame_compare = video_compare.read()
                    if not ret_compare:
                        frames_counter_compare = -1
                        break
                    else:
                        frames_counter_compare += 1
                        # Check third part of video
                        if frames_counter_compare >= ((self.total_frames / 3) * (frames_counter_orig + 1)):
                            frames_counter_compare = -1
                            break
                        # When once same part was found, to don't start check from the beginning
                        if frames_counter_compare >= frames_flag:
                            # Check that frames same and put flag of same frame and flag to skip reopening
                            if self.difference_gray_image(frame_orig, frame_compare):
                                same_frames_time_orig.append(frames_counter_orig)
                                same_frames_time_compare.append(frames_counter_compare)
                                frames_flag = frames_counter_compare
                                skip_opening = True
                                cv2.imwrite(
                                    f'{frames_counter_orig}.jpg',
                                    frame_orig
                                )
                                break
                        else:
                            skip_opening = False
            else:
                break
        self.time_compared(same_frames_time_orig)
        self.time_compared(same_frames_time_compare)


start_time = time()
path = '91_Days_[04]_[AniLibria_TV]_[HDTV-Rip_720p].mkv'
video0 = Video_redactor(name=path)
video_c = '91_Days_[05]_[AniLibria_TV]_[HDTV-Rip_720p].mkv'
boards = [2880, 2885, 2880, 5760]

test = [2880, 2881, 2882, 2898, 2899, 2900, 2901, 2902, 2903, 2904, 2914, 2915, 2916, 2917, 2918, 2919, 2920, 2921, 2922, 2923, 2924, 2925, 2926, 2927, 2928, 2929, 2930, 2931, 2932, 2933, 2934, 2935, 2936, 2937, 2938, 2939, 2940, 2941, 2942, 2943, 2944, 2945, 2946, 2947, 2948, 2949, 3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009, 3010, 3011, 3012, 3013, 3014, 3015, 3016, 3017, 3018, 3019, 3020, 3021, 3022, 3023, 3024, 3025, 3026, 3027, 3028, 3029, 3030, 3031, 3032, 3033, 3034, 3035, 3036, 3037, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 3052, 3053, 3054, 3055, 3056, 3057, 3058, 3059, 3060, 3061, 3062, 3063, 3064, 3065, 3066, 3067, 3068, 3069, 3070, 3071, 3072, 3073, 3074, 3075, 3076, 3077, 3078, 3079, 3080, 3081, 3082, 3083, 3084, 3085, 3086, 3087, 3088, 3089, 3090, 3091, 3092, 3093, 3094, 3095, 3096, 3097, 3098, 3099, 3100, 3101, 3102, 3103, 3104, 3105, 3106, 3107, 3108, 3109, 3110, 3111, 3112, 3113, 3114, 3115, 3116, 3117, 3118, 3119, 3120, 3121, 3122, 3123, 3124, 3125, 3126, 3127, 3128, 3129, 3130, 3131, 3132, 3133, 3134, 3135, 3136, 3137, 3138, 3139, 3140, 3141, 3142, 3143, 3144, 3145, 3146, 3147, 3148, 3149]

video0.time_compared(test)

video0.compare_videos(video_c)

print(time() - start_time)
