import os
import concurrent.futures

import cv2
import numpy as np
from PIL import Image
from model.PULSE.pulse import PULSE


class PULSEImageProcessor:
    def __init__(self):
        self.model = PULSE(cache_dir='cache')

    def process_images(self, input_folder):
        # Get the list of subfolders and files in the input folder
        subfolders, files = self._get_subfolders_and_files(input_folder)

        # Process subfolders and files concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for subfolder in subfolders:
                subfolder_path = os.path.join(input_folder, subfolder)
                executor.submit(self._process_subfolder, subfolder_path)

            for file in files:
                file_path = os.path.join(input_folder, file)
                executor.submit(self._process_file, file_path)

    def _process_subfolder(self, input_subfolder):
        # Get the list of subfolders and files in the input subfolder
        subfolders, files = self._get_subfolders_and_files(input_subfolder)

        # Process subfolders and files recursively
        for subfolder in subfolders:
            subfolder_path = os.path.join(input_subfolder, subfolder)
            self._process_subfolder(subfolder_path)

        for file in files:
            file_path = os.path.join(input_subfolder, file)
            self._process_file(file_path)

    def _process_file(self, input_file):
        # Load the input image
        image = Image.open(input_file)

        # Apply PULSE to the image
        output_image = self.model(image)

        # Save the output image
        output_file = self._get_output_file_path(input_file)
        output_image.save(output_file)

    def _get_output_file_path(self, input_file):
        input_dir = os.path.dirname(input_file)
        input_filename = os.path.basename(input_file)
        output_filename = f"PULSE_{input_filename}"
        output_file = os.path.join(input_dir, output_filename)
        return output_file

    def _get_subfolders_and_files(self, folder):
        subfolders = []
        files = []
        for item in os.listdir(folder):
            item_path = os.path.join(folder, item)
            if os.path.isdir(item_path):
                subfolders.append(item)
            else:
                files.append(item)
        return subfolders, files

    def process_frame(self, frame):
        # Convert the frame from BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the frame to PIL Image
        image = Image.fromarray(frame_rgb)

        # Apply PULSE to the image
        output_image = self.model(image)

        # Convert the output image to numpy array
        output_frame_rgb = np.array(output_image)

        # Convert the output frame from RGB to BGR
        output_frame_bgr = cv2.cvtColor(output_frame_rgb, cv2.COLOR_RGB2BGR)

        return output_frame_bgr
