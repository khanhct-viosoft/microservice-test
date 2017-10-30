#!/usr/bin/env python
import json
import pika
import logging
import uuid
import os
import base64
from time import sleep
from service.general import *

LOG = logging.getLogger(__name__)

class MessQ:
    def __init__(cls, messq_ip, user, password):
        cls.messq_ip = messq_ip
        cls.user = user
        cls.password = password
        credentials = pika.PlainCredentials(cls.user, cls.password)
        cls.params = pika.ConnectionParameters(cls.messq_ip, RABBITMQ_PORT , '/', credentials)
        cls.connection = pika.BlockingConnection(cls.params)
        cls.channel = cls.connection.channel()

    def on_response(cls, ch, method, props, body):
        if cls.corr_id == props.correlation_id:
            cls.response = body

    def sent_message(cls, to_queue, msg):
        try:
            attempt = 1
            while (attempt > 0) and \
                    (not cls.channel.basic_publish(exchange='',
                                                   routing_key=str(to_queue),
                                                   body=msg)):
                sleep(1)
                attempt -= 1

        except pika.exceptions.ConnectionClosed:
            cls.connection = pika.BlockingConnection(cls.params)
            cls.channel = cls.connection.channel()
            cls.channel.basic_publish(exchange='',
                                      routing_key=str(to_queue),
                                      body=msg)

        try:
            LOG.debug(" [x] Sent to queue '%s' data %s"
                          % (to_queue, json.dumps(json.loads(msg), indent=4, sort_keys=True)))
        except:
            LOG.debug(" [x] Sent to queue '%s' data %s"
                  % (to_queue, msg))

    def start_consumer(cls, worker, queue, consumer_tag=None):
        cls.channel.queue_declare(queue=queue)
        cls.channel.basic_consume(worker,
                                  queue=queue,
                                  consumer_tag=consumer_tag,
                                  no_ack=True)

        LOG.info(' [*] Waiting for messages in queue = {} and consumer_tag = {}. To exit press CTRL+C' \
              .format(queue, consumer_tag))

        #while True:
        try:
            LOG.info("Starting Consumer...........")
            cls.channel.start_consuming()
            LOG.info("Start Consumer SUCCESSFULLY.")
        except IOError as e:
            LOG.debug("Stopping Consumer ERROR {}. Start again.".format(e.message))
            return

    def stop_consumer(cls, consumer_tag=None):
        LOG.info('Stop Consummer with tag = {}'.format(consumer_tag))
        cls.channel.stop_consuming(consumer_tag)

    def delete_queue(cls, queue):
        cls.channel.queue_delete(queue)

    def send_file(cls, session, file_name, dir, to):
        LOG.info(">>>>>>>>>>>>> send file %s to %s" % (file_name, dir))
        if not os.path.isfile(file_name):
            return False
        json_msg = {}
        json_msg["SessionId"] = session
        json_msg["Command"] = "send_file"
        json_msg["Params"] = {}
        json_msg["Params"]["filepath"] = dir + '/' + os.path.basename(
            file_name)
        json_msg["From"] = "benchmark"

        with open(file_name, "rb") as f:
            encoded_string = base64.b64encode(f.read())
            f.close()
        json_msg["Params"]["content"] = encoded_string

        json_msg = json.dumps(json_msg)
        cls.sent_message(to, json_msg)
        return True
