import os

TM_QUEUE = 'tm_queue'
TM_DB    = 'tm.db'
ONBOARD_QUEUE = 'ob_queue'
YAML_DIR = '/yaml/'
CONTEXT = 'CON'
SCENARIOS = 'SCE'
ID_PREFIX = 'VIO'
TM_ADDR = '10.70.8.111'
ONBOARD_ADDR = '10.70.8.111'
BANCHMARK_ADDR = '10.70.8.111'

RABBITMQ_PORT = 5672

HOME_DIR = os.path.expanduser('~')
#HOME_DIR = ""
RESOURCE_DIR = HOME_DIR + '/.validium'

def generate_id_suffix(id):
    return '{:010d}'.format(id)

def create_reservoir():
    if not os.path.isdir(RESOURCE_DIR):
        os.makedirs(RESOURCE_DIR)
        os.makedirs(RESOURCE_DIR +  YAML_DIR)
    else:
        if not os.path.isdir(RESOURCE_DIR +  YAML_DIR):
            os.makedirs(RESOURCE_DIR + YAML_DIR)

