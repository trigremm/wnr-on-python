import getpass

import MySQLdb

from .utils import JsonDriver
from .utils import timeit

# from pkg_resources import Requirement, resource_filename
# config_file_path = resource_filename(Requirement.parse(__name__), "wnr/config/mysql_config.json")
config_path = "wnr/config/mysql_config.json"


class MysqlDriver:
    @timeit
    def __init__(self, firstrun=False, clearall=False, configpath=config_path):
        self.json = JsonDriver(configpath)
        if firstrun:
            clearall = True
            self.init_first_run()
        self.config = self.json.get_config_dict()
        self.check_if_database_exists()
        if clearall:
            self.drop_table()
        self.create_table()
        self.json = None

    def __call__(self, cmd):
        return self.pull_cmd(cmd)

    @timeit
    def init_first_run(self):
        d = {
            "user": "root",
            "host": "localhost",
            "port": 3306,
        }
        ''
        print('# initiating protocol of creation database, user and tables ...')
        ''
        while True:
            buff = getpass.getpass('mysql root password :')
            if buff:
                d['password'] = buff
                break
        ''
        buff = input('mysql host [{host}] :'.format(**d))
        if buff:
            d['host'] = buff
        ''
        buff = input('mysql port [{port}] :'.format(**d))
        if buff:
            d['port'] = buff
        ''
        config_dict = {
            "user": "hikuser",
            "password": "hikpassword",
            "host": d["host"],
            "port": d["port"],
            "db": "hikdb",
        }
        ''
        buff = input('mysql db [{db}] :'.format(**config_dict))
        if buff:
            d['db'] = buff
        ''
        buff = input('mysql db_user_name  [{user}] :'.format(**config_dict))
        if buff:
            config_dict["user"] = buff
        ''
        buff = input('mysql db_user_password  [{password}] :'.format(**config_dict))
        if buff:
            config_dict['password'] = buff
        ''
        cmd = '''DROP DATABASE IF EXISTS {db};''' \
              '''DROP USER IF EXISTS {user};''' \
              '''CREATE DATABASE {db};''' \
              '''GRANT ALL PRIVILEGES ON {db}.* to '{user}'@'{host}' identified by "{password}";''' \
              '''FLUSH PRIVILEGES;'''.format(**config_dict)
        ''
        connect = MySQLdb.connect(**d)
        cursor = connect.cursor()
        for i in cmd.split(';'):
            if i:
                print('####' + i)
                cursor.execute(i + ';')
                connect.commit()
        connect.close()
        ''
        for i in d:
            d[i] = None
        ''
        self.json.set_config_dict(config_dict)

    @timeit
    def push_cmd(self, cmd):
        print('# pushing cmd ' + cmd)
        connect = MySQLdb.connect(**self.config)
        cursor = connect.cursor()
        cursor.execute(cmd)
        connect.commit()
        connect.close()

    @timeit
    def pull_cmd(self, cmd):
        print('# pulling cmd ' + cmd)
        connect = MySQLdb.connect(**self.config)
        cursor = connect.cursor()
        cursor.execute(cmd)
        connect.commit()
        data_list = [i for i in cursor.fetchall()]
        connect.close()
        return data_list

    @timeit
    def check_if_database_exists(self):
        cmd = '''SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='{db}';'''.format(**self.config)
        data_list = self.pull_cmd(cmd)
        if not data_list:
            raise '''{db} database doesn't not exists\n'''.format(**self.config) + \
                  '''\n''' + \
                  '''to create database use following --firstrun option\n'''

    '''CONTAINER_ID, CONTAINER_CHECK_IN, PATH_TO_IMAGES'''

    @timeit
    def create_table(self):
        cmd = '''CREATE TABLE IF NOT EXISTS PSA_CONTAINERS (''' \
              '''id INT(3) NOT NULL AUTO_INCREMENT,''' \
              '''CONTAINER_ID INT(9) NOT NULL,''' \
              '''PATH_TO_IMAGES VARCHAR(255),''' \
              '''CONTAINER_CHECK_IN VARCHAR(255) ,''' \
              '''comment VARCHAR(255) ,''' \
              '''PRIMARY KEY (id)''' \
              ''') ENGINE=InnoDB DEFAULT CHARSET=utf8;'''.format(**self.config)
        self.push_cmd(cmd)

    @timeit
    def drop_table(self):
        cmd = '''DROP TABLE IF EXISTS PSA_CONTAINERS;'''.format(**self.config)
        self.push_cmd(cmd)

    @timeit
    def get_container_ids_list(self):
        cmd = '''SELECT CONTAINER_ID FROM PSA_CONTAINERS'''
        return self.pull_cmd(cmd)
