import os
from collections import defaultdict, namedtuple

import pytesseract
import zbarlight
from PIL import Image

bash_tesseract = pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class NRDriver:
    def __init__(self):
        print('# init NRDriver')

    def parse_photos_list_to_numbers_dict(self, photos_list):
        Container = namedtuple('Container', 'id type photo time')
        numbers_dict = defaultdict(Container)
        for photo in photos_list:
            id, type = self.read_qrcode(photo), 'qr'
            if not id:
                id, type = self.read_number(photo), 'img'
            if id:
                st_mtime = str(os.stat(photo).st_mtime)
                numbers_dict[photo] = Container(id, type, photo, st_mtime)
        return numbers_dict

    @staticmethod
    def read_qrcode(qr_file):
        if qr_file:
            with open(qr_file, 'rb') as image_file:
                image = Image.open(image_file)
                image.load()
            codes = zbarlight.scan_codes('qrcode', image)
            if codes:
                return codes[0].decode("utf-8")

    @staticmethod
    def read_number(num_file):
        code = pytesseract.image_to_string(Image.open(num_file))
        if len(code) == 9 and is_int(code):
            return code
