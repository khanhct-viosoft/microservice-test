#!/usr/bin/env python3
import logging
import signal
import connexion
from connexion.resolver import RestyResolver
from service.general import *
import sys

from service.dal import DAL
from service.general import *
from service.messq import MessQ
from threading import Thread

LOG = logging.getLogger(__name__)
### Microsevice version
__version__ = "0.1"
_messQ = None
thread = None

def setup_logging():
	# Add VERBOSE loglevel between DEBUG and INFO and
	logging.addLevelName(15, 'VERBOSE')

	# Add convenience function logging.verbose(...)
	logging.VERBOSE = 15

	def verbose(msg, *args, **kwargs):
		logging.log(logging.VERBOSE, msg, *args, **kwargs)

	logging.verbose = verbose

	# Add TRACE loglevel between NOTSET and DEBUG
	logging.addLevelName(5, 'TRACE')

	# Add convenience function logging.trace(...)
	logging.TRACE = 5

	def trace(msg, *args, **kwargs):
		logging.log(logging.TRACE, msg, *args, **kwargs)

	logging.trace = trace
	# Log to file and to screen
	filename= 'tm.log'
	log_format='%(asctime)-15s %(levelname)-8s %(filename)20s:%(lineno)-3d %(message)s'
	log_level = 'DEBUG'
	logOverwrite = 1
	logging.basicConfig(filename=filename,
						format=log_format,
						datefmt=None,
						level=log_level,
						filemode='w' if logOverwrite else 'a',
						)

	# define a Handler which writes INFO messages or higher to the sys.stderr
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	# set a format which is simpler for console use
	formatter = logging.Formatter(fmt='%(asctime)-8s %(levelname)-8s %(message)s',
								  datefmt='%H:%M:%S')
	# tell the handler to use this format
	console.setFormatter(formatter)
	# add the handler to the root logger
	logging.getLogger('').addHandler(console)

	logging.info("Running Task Management version %s", __version__)



def callback(ch, method, properties, body):
	LOG.info('1111111111111111111111111111111111..................')

def destroy(messQ):
	messQ.delete_queue(TM_QUEUE)
	messQ.stop_consumer()
	DAL.close_connection()

class QHandler(Thread):

	def __init__(self, thread_id, messQ):
		Thread.__init__(self)
		self.thread_id = thread_id
		self.messQ = messQ

	def run(self):
		self.messQ.start_consumer(callback, TM_QUEUE)

def signal_handler(signal, frame):
    global _messQ
    LOG.info('You pressed Ctrl+C!')
    #destroy(_messQ)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
#_messQ = MessQ(TM_ADDR)
# setup log controller
setup_logging();
# create reservoir to contain the resource of app
create_reservoir()
# init database
DAL.init()
#q = QHandler('1', _messQ)
#q.start()
app = connexion.App(__name__)
app.add_api('swagger/tm.yaml', resolver=RestyResolver('api'))

# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app
if __name__ == '__main__':
	# run our standalone gevent server
	app.run(port=9090, server='gevent')



