import os
import subprocess
import sys

import requests

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import utils

test_search_context = 'TestSearchContext'

import unittest

session = requests.Session()


def get_test_search_context():
    return {
        "name": test_search_context,
        "matchers": [
            {
                "name": "SsnMatcher",
                "type": "pattern",
                "pattern": r"\b(\d{3}[-]?\d{2}[-]?\d{4})\b"
            },
            {
                "name": "EmailMatcher",
                "type": "pattern",
                "pattern": r"\b[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,4}\b"
            },
        ]
    }


def test_demos(demo_folder_name, demo_program_name):
    text_files_demo_dir = os.path.join(parent_dir, demo_folder_name)
    os.chdir(text_files_demo_dir)
    subprocess.run(f'python {demo_program_name}', check=True)


class Testing(unittest.TestCase):

    def test_create_context(self):
        try:
            utils.create_context('searchContext', get_test_search_context(), session)
        except Exception as err:
            self.fail('Unexpected exception {}'.format(err))

    def test_destroy_context(self):
        try:
            utils.destroy_context('searchContext', test_search_context, session)
        except Exception as err:
            self.fail('Unexpected exception {}'.format(err))

    def test_text_demo(self):
        try:
            test_demos('text-files', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'Text-files demo failed.\n{e}')

    def test_x12_demo(self):
        try:
            test_demos('x12', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'x12 demo failed.\n{e}')

    def test_pdf_image_demo(self):
        try:
            test_demos('pdf-image', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'pdf-image demo failed.\n{e}')

    def test_parquet_demo(self):
        try:
            test_demos('parquet', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'parquet demo failed.\n{e}')

    def test_microsoft_excel_and_word_demo(self):
        try:
            test_demos('microsoft-excel-and-word', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'microsoft-excel-and-word demo failed.\n{e}')

    def test_json_xml_demo(self):
        try:
            test_demos('json-xml', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'json-xml demo failed.\n{e}')

    def test_hl7_demo(self):
        try:
            test_demos('hl7', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'hl7 demo failed.\n{e}')

    def test_fixed_width_demo(self):
        try:
            test_demos('fixed-width', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'fixed-width demo failed.\n{e}')

    def test_dicom_demo(self):
        try:
            test_demos('dicom', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'dicom demo failed.\n{e}')

    def test_csv_tsv_demo(self):
        try:
            test_demos('csv-tsv', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'csv-tsv demo failed.\n{e}')


if __name__ == '__main__':
    unittest.main()