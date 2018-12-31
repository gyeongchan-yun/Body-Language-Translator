import os
from configparser import ConfigParser

dir_path = os.path.dirname(os.path.realpath(__file__))

config = ConfigParser()
config.read(dir_path + '/../config/config.conf')
