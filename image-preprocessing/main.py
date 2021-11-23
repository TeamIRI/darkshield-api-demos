import cv2 as cv2
from PIL import Image
import json
import logging
import os
import sys
import argparse
import requests
import pathlib
import math
#    Image preprocessing for the DarkShield-Files API:
# Program to pre-process images through rescaling and deskewing pipelines, send to the DarkShield-Files API,
# and then postprocess to revert preprocessing changes. Other pipelines could be added to this framework
# to further bolster for specific needs.

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from requests_toolbelt import MultipartEncoder
from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget
from utils import base_url
masked_folder = "masked"
original_height = 0
original_width = 0
original_angle = 0


def is_image_extension(file_name):
    return file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff'))


# Rotate the image around its center
def rotate_image(cv_image, angle: float):
    new_image = cv_image.copy()
    (h, w) = new_image.shape[:2]
    center = (w // 2, h // 2)
    m = cv2.getRotationMatrix2D(center, angle, 1.0)
    new_image = cv2.warpAffine(new_image, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return new_image


# Calculate skew angle of an image
def get_skew_angle(cv_image) -> float:
    # Prep image, copy, convert to gray scale, blur, and threshold
    new_image = cv_image.copy()
    gray = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Apply dilate to merge text into meaningful lines/paragraphs.
    # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
    # But use smaller kernel on Y axis to separate between different blocks of text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=5)

    # Find all contours
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Find largest contour and surround in min area box
    largest_contour = contours[0]
    min_area_rect = cv2.minAreaRect(largest_contour)

    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = min_area_rect[-1]
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle


def revert_deskew(cv_image):
    global original_angle
    if original_angle == 0:  # no need to revert
        return cv_image
    return rotate_image(cv_image, 1.0 * original_angle)


# Deskew image
def deskew(cv_image, args):
    global original_angle
    angle = get_skew_angle(cv_image)
    if angle < args.skew_angle:
        original_angle = 0
        return cv_image
    original_angle = angle
    return rotate_image(cv_image, -1.0 * angle)


def revert_resize(image, args):
    if args.width / original_width < 1:
        return image
    return image.resize((original_width, original_height))


def resize(image, args):
    width, height = image.size
    global original_height
    global original_width
    original_width = width
    original_height = height
    scale = args.width / width
    if scale < 1:  # don't resize; reducing size removes some part of the image.
        return image
    new_width = math.ceil(width * scale)
    new_height = math.ceil(height * scale)
    resized_image = image.resize((new_width, new_height))
    return resized_image


def post_process(img_name, args):
    logging.info(f"Postprocessing {img_name}...")
    image = revert_resize(Image.fromarray(cv2.cvtColor(revert_deskew(cv2.imread(img_name)), cv2.COLOR_BGR2RGB)), args)
    image.save(img_name)


def pre_process(img_name, args):
    logging.info(f"Preprocessing {img_name}...")
    image = resize(Image.fromarray(cv2.cvtColor(deskew(cv2.imread(img_name), args), cv2.COLOR_BGR2RGB)), args)
    parts = pathlib.Path(img_name).parts
    final_path = ""
    for i, part in enumerate(parts):
        if i < len(parts) - 1:
            final_path = final_path + part + os.sep
        else:
            final_path = final_path + f"prep-{part}"
    image.save(final_path)
    return final_path


def absolute_file_paths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


def send_file_to_darkshield_api(file_name, args):
    pre_processed_file_name = pre_process(file_name, args)
    base_name = os.path.basename(pre_processed_file_name)
    with open(pre_processed_file_name, 'rb') as f:
        os.makedirs(masked_folder, exist_ok=True)
        encoder = MultipartEncoder(fields={
            'context': ('context', context, 'application/json'),
            'file': (base_name, f)
        })
        logging.info(f"POST: sending '{base_name}' to {url}")
        with session.post(url, data=encoder, stream=True,
                          headers={'Content-Type': encoder.content_type}) as r:
            if r.status_code >= 300:
                raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
            logging.info(f"Extracting '{base_name}' and 'results.json' into {masked_folder}.")
            parser = StreamingFormDataParser(headers=r.headers)
            parser.register('file', FileTarget(f'{masked_folder}/{base_name}'))
            parser.register('results', FileTarget(f'{masked_folder}/{base_name}-results.json'))
            for chunk in r.iter_content(4096):
                parser.data_received(chunk)
    os.remove(pre_processed_file_name)
    post_process(f'{masked_folder}/{base_name}', args)


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    session = requests.Session()
    parser = argparse.ArgumentParser(description='Demo for preprocessing images in a folder.')
    exclusive_group = parser.add_mutually_exclusive_group(required=True)
    exclusive_group.add_argument('-d', '--directory', metavar='name', type=str, help='Specify a directory containing '
                                                                                     'images to be preprocessed.')
    exclusive_group.add_argument('-f', '--file', metavar='name', type=str,
                                 help='Specify a single image file to be preprocessed.')
    parser.add_argument('-w', '--width', type=int,
                        help='Images larger than the width in pixels specified will not be rescaled. (default 1600 '
                             'pixels)', default=1600)
    parser.add_argument('-a', '--skew-angle', type=int,
                        help='Only images that are skewed by the angle specified or greater will be run through '
                             'deskewing processing. (default 5)', default=5)
    args = parser.parse_args()

    try:
        setup(session)
        url = f'{base_url}/files/fileSearchContext.mask'
        context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name
        })
        if args.directory:
            filenames = absolute_file_paths(args.directory)
            logging.info(filenames)
            for filename in filenames:
                if is_image_extension(filename):
                    logging.info(filename)
                    send_file_to_darkshield_api(filename, args)
        elif args.file:
            if is_image_extension(args.file):
                send_file_to_darkshield_api(args.file, args)
    finally:
        teardown(session)
