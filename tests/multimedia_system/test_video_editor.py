import hashlib
import os
from unittest import TestCase
import json
import ffmpeg

from multimedia_system.video_editor import VideoEditor
from dotenv import load_dotenv

load_dotenv()
project_dir = os.environ['WORK_DIRECTORY']


def compute_hash(filename):
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


class TestVideoEditor(TestCase):

    def setUp(self) -> None:
        # TODO: edit 3 videos with different params and edit json with this params:
        #  [same frames, nothing]
        with open(f"{project_dir}tests/resources/video_editor/test_video_editor.json", "r") as file:
            self.json_test = json.load(file)
        self.video0 = f'{project_dir}tests/resources/video_editor/test_video_0.mp4'
        self.video1 = f'{project_dir}tests/resources/video_editor/test_video_1.mp4'
        self.video_editor = VideoEditor(self.video0)
        self.video_editor1 = VideoEditor(self.video1)
        self.video_start_test = f"{project_dir}tests/resources/video_editor/test_start_video_0.mp4"
        self.video_mid_test = f"{project_dir}tests/resources/video_editor/test_mid_video_0.mp4"
        self.video_end_test = f"{project_dir}tests/resources/video_editor/test_end_video_0.mp4"
        self.black_screen_duration = 5
        self.mid_test_start = 15

    def test_get_video_data(self):
        video_name, video_format = os.path.splitext(os.path.basename(self.video0))
        self.assertTrue(self.video_editor.short_name == video_name)
        self.assertTrue(self.video_editor.global_path == f"{project_dir}tests/resources/video_editor/")
        self.assertTrue(self.video_editor.format == video_format)
        self.assertTrue(self.video_editor.fps == 30)
        self.assertTrue(self.video_editor.height == 714)
        self.assertTrue(self.video_editor.width == 1280)
        self.assertTrue(self.video_editor.total_frames == 899)
        self.assertTrue(self.video_editor.reserve_compare == 60)
        self.assertTrue(self.video_editor.reserve_time_compare == 180)
        self.assertTrue(self.video_editor.reserve_duration == 3000)

    def create_start_video(self):
        (
            ffmpeg.input(self.video0)
            .filter('tpad', start_duration=self.black_screen_duration)
            .output(self.video_start_test)
            .overwrite_output()
            .run()
        )

    def create_mid_video(self):
        (
            ffmpeg.concat(
                ffmpeg.input(self.video0, to=self.mid_test_start),
                ffmpeg.input(self.video0, ss=self.mid_test_start)
                .filter('tpad', start_duration=self.black_screen_duration))
            .output(self.video_mid_test)
            .overwrite_output()
            .run()
        )

    def create_end_video(self):
        # TODO: need to make test vido with 5sec at end
        (
            ffmpeg.concat(
                ffmpeg.input(self.video0),
                ffmpeg
                .input(f'color=color=black:'
                       f's={self.video_editor.width}x{self.video_editor.height}:d={self.black_screen_duration}',
                       f='lavfi')
            )
            .output(self.video_end_test)
            .overwrite_output()
            .run()
        )

    def test_compare_videos_fast_start_video(self):
        # Create video with 5 sec black screen at start
        if not os.path.exists(self.video_start_test):
            self.create_start_video()
        self.assertTrue(self.video_editor.compare_videos_fast(self.video_start_test,
                                                              [0, self.video_editor.total_frames],
                                                              [0, VideoEditor(self.video_start_test).total_frames])
                        == self.json_test["result_compare_videos_fast_start_video_0"])

    def test_compare_videos_fast_mid_video(self):
        # Create video with 5 sec black screen in mid
        if not os.path.exists(self.video_mid_test):
            self.create_mid_video()
        self.assertTrue(self.video_editor.compare_videos_fast(self.video_mid_test,
                                                              [0, self.video_editor.total_frames],
                                                              [0, VideoEditor(self.video_mid_test).total_frames])
                        == self.json_test["result_compare_videos_fast_mid_video_0"])

    def test_compare_videos_fast_end_video(self):
        # Create video with 5 sec black screen at end
        if os.path.exists(self.video_end_test):
            self.create_end_video()

    def test_time_fine_one_par(self):
        time_result = [[2, 10], [0, 9], [15, 24]]
        self.assertTrue(self.video_editor.time_find_one_par(self.json_test['test_time_compare_0']) == time_result[0])
        self.assertTrue(self.video_editor.time_find_one_par(self.json_test['test_time_compare_1']) == time_result[1])
        self.assertTrue(self.video_editor.time_find_one_par(self.json_test['test_time_compare_2']) == time_result[2])

    def test_compare_videos_fast_same(self):
        self.assertTrue(self.video_editor.compare_videos_fast(
            self.video0, [0, self.video_editor.total_frames], [0, self.video_editor.total_frames])
                        == self.json_test['result_same_video0']
                        )

    def test_slice_video(self):
        # TODO: Find another way to different them(use exist my method to fast compare videos)
        if not os.path.exists(self.video_start_test):
            self.create_start_video()
        VideoEditor(self.video_start_test).slice_video([0, self.black_screen_duration])
        print(compute_hash(
            f"{project_dir}tests/resources/video_editor/test_start_video_0_edonssfall.mp4") == compute_hash(self.video0)
                        )
        if not os.path.exists(self.video_mid_test):
            self.create_mid_video()
        VideoEditor(self.video_mid_test).slice_video(
            [self.mid_test_start, self.mid_test_start + self.black_screen_duration]
        )
        print(compute_hash(
            f"{project_dir}tests/resources/video_editor/test_mid_video_0_edonssfall.mp4") == compute_hash(self.video0)
                        )
