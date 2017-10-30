from api.yaml_parser import *
#from flask_injector import inject
from flask import jsonify, Response, stream_with_context
from service.dal import DAL
from service.general import *
from service.task import Task
import logging
from service.messq  import MessQ
import os
import uuid
LOG = logging.getLogger(__name__)

class Handler(object):
    messQ = None
    #@inject
    def __init__(self):
        self.messQ = MessQ(ONBOARD_ADDR, 'root', '1')

    def post(self, yaml_file):
        extensions = ['.zip', '.gz', '.tar']
        LOG.info('Receive a file %s from: ', (yaml_file.filename))
        extension = os.path.splitext(yaml_file.filename)[1]
        LOG.info(extension)
        if extension in extensions:
            LOG.debug('Writing file.......')
            yaml_file.save(RESOURCE_DIR + YAML_DIR + yaml_file.filename)
            yaml_file.close()
            id = str(uuid.uuid4())[-8:]
            task_id = ID_PREFIX + id
            context_id = ID_PREFIX  + CONTEXT + id
            scenarios_id = ID_PREFIX  + SCENARIOS + id
            content = RESOURCE_DIR + YAML_DIR + yaml_file.filename
            task = Task(task_id, context_id, scenarios_id, str(content))
            DAL.add_task(task)
            ret = DAL.get_all_tasks()
            LOG.info(ret)
            msg = {
                'code': 'YAR_200',
                'task_id': task_id
            }
            self.messQ.sent_message(ONBOARD_QUEUE, str(msg))
            LOG.info("Success code 200: Upload file %s successfully." % (yaml_file.filename))
            return {"Success": "Upload file %s successfully." % (yaml_file.filename)}, 200
        else:
            LOG.debug("Error code 400: Making sure the format of file uploaded is yaml. Thanks!")
            return {"Error": "Making sure the format of file uploaded is yaml."}, 400

    def post1(self, yaml_file):
        LOG.info('Receive a file %s from: ', (yaml_file.filename))
        if yaml_file.filename.endswith('.yaml'):
            LOG.debug('Writing file.......')
            yaml_file.save(RESOURCE_DIR + YAML_DIR + yaml_file.filename)
            yaml_file.close()
            id = str(uuid.uuid4())[-8:]
            task_id = ID_PREFIX + id
            context_id = ID_PREFIX + CONTEXT + id
            scenarios_id = ID_PREFIX + SCENARIOS + id
            content = RESOURCE_DIR + YAML_DIR + yaml_file.filename
            task = Task(task_id, context_id, scenarios_id, str(content))
            DAL.add_task(task)
            msg = {
                'code': 'VIO_200',
                'task_id': task_id
            }
            self.messQ.sent_message(ONBOARD_QUEUE, str(msg))
            LOG.debug("Success code 200: Upload file %s successfully." % (yaml_file.filename))
            return {"Success": "Upload file %s successfully." % (yaml_file.filename)}, 200
        else:
            LOG.debug("Error code 400: Making sure the format of file uploaded is yaml. Thanks!")
            return {"Error": "Making sure the format of file uploaded is yaml."}, 400

    def get(self, task_id):
        LOG.info('Receive a request')
        row = DAL.get_task_info(task_id)
        if row != None:
            yaml_path = row[3]
            if not os.path.isfile(yaml_path):
                return {"Error": "data do not exist."}, 400
            with open(yaml_path, 'rb') as f:
                resp = Response(stream_with_context(f.read()), mimetype='application/gzip')
            resp.headers["Content-Disposition"] = "attachment; filename={0}".format(os.path.basename(yaml_path))
            resp.headers['FileName'] = os.path.basename(yaml_path)
            resp.headers["Content-type"] = "text/csv"
            return resp, 200
        return {"Error": "task_id: %s does not exist." % (task_id)}, 400
class_instance = Handler()




