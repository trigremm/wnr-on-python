import os
import shutil
from os.path import expanduser

from .utils import JsonDriver
from .utils import timeit

# from pkg_resources import Requirement, resource_filename
# config_file_path = resource_filename(Requirement.parse(__name__), "wnr/config/shell_config.json")
config_path = "wnr/config/shell_config.json"
img_ext_list = ['.jpg', '.jpeg', '.bmp', '.png', '.tiff']


@timeit
def mkdir(dname):
    assert dname
    if dname and not os.path.exists(dname):
        os.makedirs(dname)


@timeit
def touch(fname, times=None):
    assert fname
    with open(fname, 'a'):
        os.utime(fname, times)


@timeit
def get_ext(fname):
    _, ext = os.path.splitext(fname)
    return ext


@timeit
def get_files_list(path):
    assert path
    files_list = list()
    for data_file in os.listdir(path):
        if not data_file:
            continue
        data_path = path + '/' + data_file
        if os.path.isfile(data_path):
            files_list += [data_path]
        elif os.path.isdir(data_path):
            files_list += get_files_list(data_path)
    return files_list


class ShellDriver:
    @timeit
    def __init__(self, firstrun=False, clearall=False, configpath=config_path):
        self.json = JsonDriver(configpath)
        if firstrun:
            self.init_firstrun()
            clearall = True
        self.config = self.json.get_config_dict()
        self.create_dirs()
        if clearall:
            self.clear_dirs()
        self.json = None

    def init_firstrun(self):
        home = expanduser('~')
        d = {
            'input_dir': home + '/hikvision/192.168.1.64/',
            'output_dir': home + '/hikvision/192.168.1.64_codes/',
            'archive_dir': home + '/hikvision/192.168.1.64_archive/',
        }
        ''
        print('# if following dirs are not exist, they will be created')
        ''
        buff = input('full path to input_dir [{input_dir}] :'.format(**d))
        if buff:
            d['input_dir'] = buff
        ''
        buff = input('full path to output_dir [{output_dir}] :'.format(**d))
        if buff:
            d['output_dir'] = buff
        ''
        buff = input('full path to archive_dir [{archive_dir}] :'.format(**d))
        if buff:
            d['archive_dir'] = buff
        ''
        self.json.set_config_dict(d)

    @timeit
    def create_dirs(self):
        for dname, dpath in self.config.items():
            if dname.endswith('_dir'):
                mkdir(dpath)

    @timeit
    def clear_dirs(self):
        files_list = list()
        for dname, dpath in self.config.items():
            if dname.endswith('_dir'):
                files_list += get_files_list(dpath)
        for fname in files_list:
            os.remove(fname)

    @timeit
    def get_photos_list(self):
        files_list = get_files_list(self.config['input_dir'])
        photos_list = [photo for photo in files_list if get_ext(photo) in img_ext_list]
        return photos_list

    @staticmethod
    @timeit
    def save_photo(photo_location, photo_destination):
        shutil.move(photo_location, photo_destination)

    @timeit
    def archive_photos_list(self, photos_list):
        for photo in photos_list:
            try:
                shutil.move(photo, self.config['archive_dir'])
            except:
                os.remove(photo)
