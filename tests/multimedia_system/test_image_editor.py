import os

import cv2
import numpy as np
from multimedia_system.image_editor import PULSEImageProcessor
from dotenv import load_dotenv

import unittest


load_dotenv()
project_dir = os.environ['PROJECT_DIR']
resources = f'{project_dir}/tests/resources/image_editor'


class PULSEImageProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.processor = PULSEImageProcessor()

    def test_process_images(self):
        input_folder = f"{resources}/test"
        self.processor.process_images(input_folder)

        subfolders, files = self.processor._get_subfolders_and_files(input_folder)

        for subfolder in subfolders:
            subfolder_path = os.path.join(input_folder, subfolder)
            output_subfolder_path = os.path.join(f"{resources}/test_passed", subfolder)
            self.assertTrue(os.path.exists(output_subfolder_path))

            subfolder_files = self.processor._get_subfolders_and_files(subfolder_path)[1]
            output_subfolder_files = self.processor._get_subfolders_and_files(output_subfolder_path)[1]
            self.assertEqual(len(subfolder_files), len(output_subfolder_files))

        for file in files:
            file_path = os.path.join(input_folder, file)
            output_file_path = os.path.join(f"{resources}/test_passed", file)
            self.assertTrue(os.path.exists(output_file_path))

    def test_process_frame(self):
        frame = cv2.imread(f"{resources}/test/frame.jpg")

        output_frame = self.processor.process_frame(frame)

        self.assertIsNotNone(output_frame)
        self.assertIsInstance(output_frame, np.ndarray)
        self.assertEqual(frame.shape, output_frame.shape)

    def tearDown(self):
        # Clean up the output folder
        output_folder = f"{resources}/test_passed"
        subfolders, files = self.processor._get_subfolders_and_files(output_folder)

        for subfolder in subfolders:
            subfolder_path = os.path.join(output_folder, subfolder)
            for file in os.listdir(subfolder_path):
                file_path = os.path.join(subfolder_path, file)
                os.remove(file_path)
            os.rmdir(subfolder_path)

        for file in files:
            file_path = os.path.join(output_folder, file)
            os.remove(file_path)
