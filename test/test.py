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
            test_demos('pdf-image/basic', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'basic pdf-image demo failed.\n{e}')

    def test_pdf_form(self):
        try:
            test_demos('pdf-image/application-form', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'PDF form demo failed.\n{e}')

    def test_check_image_demo(self):
        try:
            test_demos('pdf-image/check', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'Check image demo failed.\n{e}')

    def test_credit_card_image_demo(self):
        try:
            test_demos('pdf-image/credit-card', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'Credit card image demo failed.\n{e}')

    def test_credit_card_image_bounding_box_demo(self):
        try:
            test_demos('pdf-image/credit-card/boundingbox', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'Credit card image bounding box demo failed.\n{e}')

    def test_image_text_replacement_demo(self):
        try:
            test_demos('pdf-image/image-text-replacement', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'image-text-replacement demo failed.\n{e}')

    def test_application_form_generation_demo(self):
        try:
            test_demos('test-data-generation/application-form-generation', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'Application form generation demo failed.\n{e}')

    def test_application_form_generation_demo(self):
        try:
            test_demos('test-data-generation/check-generation', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'Check generation demo failed.\n{e}')

    def test_application_form_generation_demo(self):
        try:
            test_demos('test-data-generation/credit-card-generation', 'main.py')
        except subprocess.CalledProcessError as e:
            self.fail(f'Credit card generation demo failed.\n{e}')

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