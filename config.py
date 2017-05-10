# --*-- coding: UTF-8 --*--

import os
import sys

import trafaret as t
from trafaret_config import read_and_validate
from trafaret_config import ConfigError


MAILCHIMP_TRAFARET = t.Dict({
    'app_key': t.String(),
    'username': t.String(),
    'lists_ids': t.List(t.String())
})

MYSQL_TRAFARET = t.Dict({
    'user': t.String(),
    'host': t.String(),
    'port': t.Int(),
    'dbname': t.String()
})

CONFIG_TRAFARET = t.Dict({
    'mailchimp': MAILCHIMP_TRAFARET,
    'mysql': MYSQL_TRAFARET
})


def init_config():
    config_filename = os.environ.get("CONFIG_NAME", "dev.yaml")
    config = process_config_file(config_filename)
    return config

def process_config_file(filename):
    try:
        cwd = os.getcwd()
        config = read_and_validate(os.path.join(cwd, filename), CONFIG_TRAFARET)
    except ConfigError as e:
        print(e)
        sys.exit(1)
    return config
