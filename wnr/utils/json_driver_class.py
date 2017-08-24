import json


class JsonDriver:
    def __init__(self, config_path):
        print ('# init JsonDriver ' + config_path)
        self.__config_path = config_path

    def __call__(self):
        return self.get_config_dict()

    def get_config_path(self):
        return self.__config_path

    def set_config_path(self, config_path):
        self.__config_path = config_path

    def get_config_dict(self):
        try:
            with open(self.__config_path) as fp:
                config_dict = json.load(fp)
            return config_dict
        except:
            raise 'Oops!, reading {} json file error '.format(self.__config_path)

    def set_config_dict(self, config_dict):
        try:
            with open(self.__config_path, 'w') as fp:
                json.dump(config_dict, fp, sort_keys=True, indent=4)
        except:
            raise 'Oops!, writing json to {} file error '.format(self.__config_path)
