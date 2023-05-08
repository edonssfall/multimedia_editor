import os
from unittest import TestCase
import json
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
        self.video2 = f'{project_dir}tests/resources/video_editor/test_video_2.mp4'
        self.video3 = f'{project_dir}tests/resources/video_editor/test_video_3.mp4'
        self.video4 = f'{project_dir}tests/resources/video_editor/test_video_4.mp4'
        self.video_editor = VideoEditor(self.video0)
        self.video_editor1 = VideoEditor(self.video1)
        self.video_editor2 = VideoEditor(self.video2)
        self.video_editor3 = VideoEditor(self.video3)
        self.video_editor4 = VideoEditor(self.video4)

    def test_get_video_data(self):
        print(self.video_editor.short_name)
        self.assertTrue(self.video_editor.short_name == 'test_video_0')
        self.assertTrue(self.video_editor.fps == 30)
        self.assertTrue(self.video_editor.resolution == 714)
        self.assertTrue(self.video_editor.total_frames == 2693)
        self.assertTrue(self.video_editor.reserve_compare == 60)
        self.assertTrue(self.video_editor.reserve_time_compare == 150)
        self.assertTrue(self.video_editor.reserve_duration == 3000)

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
        print(self.video_editor.compare_videos_fast(self.video2,
                                                    [0, self.video_editor.total_frames],
                                                    [0, self.video_editor2.total_frames]))

    def test_video_duration_fast(self):
        print(self.video_editor.video_duration_fast(
            self.video1, [0, self.video_editor.total_frames], [0, self.video_editor1.total_frames])
        )
