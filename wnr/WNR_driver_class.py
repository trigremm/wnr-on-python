#!/usr/bin/python3
import sys
import time

from wnr.NR_driver_class import NRDriver
from wnr.mysql_driver_class import MysqlDriver
from wnr.shell_driver_class import ShellDriver
from wnr.utils.get_time import get_time
from wnr.utils.timeit_decorator import timeit


def get_difference_list(a, b):
    c = [i for i in a if i not in b]
    return c


def str_len(a):
    b = str(len(a))
    return b


class WNRDrive:
    def __init__(self):
        first_run_flag = True if '--firstrun' in sys.argv else False
        clear_all_flag = True if '--clearall' in sys.argv else False
        self.shell = ShellDriver(firstrun=first_run_flag, clearall=clear_all_flag)
        self.mysql = MysqlDriver(firstrun=first_run_flag, clearall=clear_all_flag)
        self.NR = NRDriver()

    def __call__(self):
        while True:
            self.main()
            time.sleep(5)

    def main(self):
        photos_list = self.shell.get_photos_list()
        if not photos_list:
            return
        else:
            self.update_log('step 1 :' + str_len(photos_list) + ' photos in queue')
        ''
        numbers_dict = self.NR.parse_photos_list_to_numbers_dict(photos_list)
        empty_photos_list = get_difference_list(photos_list, numbers_dict)
        if empty_photos_list:
            self.shell.archive_photos_list(empty_photos_list)
            self.update_log(str_len(empty_photos_list) + ' photos moved to archive_dir')
        if not numbers_dict:
            return
        else:
            self.update_log('step 2 :' + str_len(numbers_dict) + ' numbers in queue')
        ''
        unique_numbers_dict = self.filter_numbers_dict(numbers_dict)
        empty_photos_list = get_difference_list(numbers_dict, unique_numbers_dict)
        if empty_photos_list:
            self.shell.archive_photos_list(empty_photos_list)
            self.update_log(str_len(empty_photos_list) + ' photos moved to trash_dir')
        if not unique_numbers_dict:
            return
        else:
            self.update_log('step 3 :' + str_len(unique_numbers_dict) + ' uniques in queue')
        ''
        self.save_photos_and_update_database(unique_numbers_dict)

    def update_log(self, message):
        print('# ' + message)
        # self.shell.update_log(message)
        # self.mysql.update_log(message)

    '''CONTAINER_ID, CONTAINER_CHECK_IN, PATH_TO_IMAGES'''

    def filter_numbers_dict(self, numbers_dict):
        ids_list = [str(i[0]) for i in self.mysql.get_container_ids_list()]
        unique_numbers_dict = dict()
        for key in numbers_dict:
            value = numbers_dict[key].id
            self.update_log('ids_list :' + str(ids_list))
            self.update_log('value :' + str(value))
            if value not in ids_list and str(value) not in ids_list:
                unique_numbers_dict[key] = numbers_dict[key]
                ids_list += [value] + [str(value)]
        return unique_numbers_dict

    @timeit
    def save_photos_and_update_database(self, unique_numbers_dict):
        cmd = """INSERT INTO PSA_CONTAINERS (CONTAINER_ID, CONTAINER_CHECK_IN, PATH_TO_IMAGES) VALUES("{CONTAINER_ID}", "{CONTAINER_CHECK_IN}", "{PATH_TO_IMAGES}")"""
        # numbers_dict[photo] += [(number, type, photo, st_mtime)]
        for photo in unique_numbers_dict:
            (number, type, photo_loc, st_mtime) = unique_numbers_dict[photo]
            photo_dest = self.shell.config['output_dir'] + number + '.jpg'
            d = {'CONTAINER_ID': number, 'CONTAINER_CHECK_IN': get_time(), 'PATH_TO_IMAGES': photo_dest}
            self.shell.save_photo(photo_loc, photo_dest)
            insert_value_cmd = cmd.format(**d)
            self.mysql.push_cmd(insert_value_cmd)
            self.update_log('+++ photo moved to output_dir: ' + photo_loc + ' as ' + number + '.jpg')
