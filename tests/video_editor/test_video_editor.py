import os
from unittest import TestCase
import json
import ffmpeg

from video_system.video_editor import VideoEditor
from dotenv import load_dotenv

load_dotenv()
project_dir = os.environ['WORK_DIRECTORY']


class TestVideoEditor(TestCase):

    def setUp(self) -> None:
        # TODO: edit 3 videos with different params and edit json with this params:
        #  [nothing, same frames],
        #  [same frames, nothing, same frames],
        #  [same frames, nothing]
        with open(f"{project_dir}tests/resources/video_editor/test_video_editor.json", "r") as file:
            self.json_test = json.load(file)
        self.video0 = f'{project_dir}tests/resources/video_editor/test_video_0.mp4'
        self.video1 = f'{project_dir}tests/resources/video_editor/test_video_1.mp4'
        self.video_editor = VideoEditor(self.video0)
        self.video_editor1 = VideoEditor(self.video1)

    def test_get_video_data(self):
        print(self.video_editor.short_name)
        self.assertTrue(self.video_editor.short_name == 'test_video_0')
        self.assertTrue(self.video_editor.fps == 30)
        self.assertTrue(self.video_editor.resolution == 714)
        self.assertTrue(self.video_editor.total_frames == 2693)
        self.assertTrue(self.video_editor.reserve_compare == 60)
        self.assertTrue(self.video_editor.reserve_time_compare == 150)
        self.assertTrue(self.video_editor.reserve_duration == 3000)

    def test_video_create(self):
        start_test = f"{project_dir}tests/resources/video_editor/test_start_video_0.mp4"
        mid_test = f"{project_dir}tests/resources/video_editor/test_mid_video_0.mp4"
        end_test = f"{project_dir}tests/resources/video_editor/test_end_video_0.mp4"
        black_screen_duration, mid_test_start = 5, 60
        # Create video at start 5 sec of black screen
        (
            ffmpeg.input(self.video0)
            .filter('tpad', start_duration=black_screen_duration)
            .output(start_test)
            .overwrite_output()
            .run()
        )
        # Create video 5 sec of black screen after 60 secs
        (
            ffmpeg.concat(
                ffmpeg.input(self.video0, to=mid_test_start),
                ffmpeg.input(self.video0, ss=mid_test_start)
                .filter('tpad', start_duration=black_screen_duration))
            .output(mid_test)
            .overwrite_output()
            .run()
        )
        # TODO: need to make test vido with 5sec at end
        (
            ffmpeg.input(self.video0).filter('tpad', stop_duration=black_screen_duration).output(end_test).overwrite_output().run()
        )

    def test_time_compare(self):
        # TODO: more testcases for json
        time_result = [[2, 10], [15, 24]]
        self.assertTrue(self.video_editor.time_find_one_par(self.json_test['test_time_compare0']) == time_result[0])

    def test_compare_videos_fast_same(self):
        self.assertTrue(self.video_editor.compare_videos_fast(
            self.video0, [0, self.video_editor.total_frames], [0, self.video_editor.total_frames])
                        == self.json_test['result_same_video0']
                        )
        self.assertTrue(self.video_editor.compare_videos_fast(
            self.video1, [0, self.video_editor.total_frames], [0, self.video_editor.total_frames])
                        == self.json_test['result_same_video0']
                        )

    def test_compare_videos_fast_different(self):
        print(self.video_editor.compare_videos_fast(self.video1,
                                                    [0, self.video_editor.total_frames],
                                                    [0, self.video_editor1.total_frames]))

    def test_video_duration_fast(self):
        print(self.video_editor.video_duration_fast(
            self.video1, [0, self.video_editor.total_frames], [0, self.video_editor1.total_frames])
        )
