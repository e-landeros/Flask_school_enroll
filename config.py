import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'\x07\x11\xdc\xf0&J{\x92r\x17U\xc7\xda\xbaH\t'

    MONGODB_SETTINGS = {'db': 'UTA_Enrollment'}
