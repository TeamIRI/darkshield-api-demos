import io
import json
import logging
import os
import signal
import sys
import time

import requests

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from kafka import KafkaConsumer, KafkaProducer
from multiprocessing import Process
from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget
from utils import base_url

bootstrap_servers = 'localhost:9092'
source_topic = 'darkshield-demo'
masked_topic = 'darkshield-demo-masked'
result_topic = 'darkshield-demo-results'


def consume_events(session):
    logging.info('Started consumer.')
    url = f'{base_url}/files/fileSearchContext.mask'
    context = json.dumps({
        "fileSearchContextName": file_search_context_name,
        "fileMaskContextName": file_mask_context_name
    })

    consumer = KafkaConsumer(source_topic, bootstrap_servers=bootstrap_servers)
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
    for message in consumer:
        logging.info('Consumer: Read message.')
        logging.info("Consumer: sending message to %s", url)
        files = {
            'context': context,
            'file': ('message.json', io.BytesIO(message.value), 'application/json')
        }
        with session.post(url, files=files) as r:
            if r.status_code >= 300:
                raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")

            parser = StreamingFormDataParser(headers=r.headers)
            masked = ValueTarget()
            results = ValueTarget()
            parser.register('file', masked)
            parser.register('results', results)
            for chunk in r.iter_content(4096):
                parser.data_received(chunk)

            logging.info('Consumer: Sending masked data to "%s"...', masked_topic)
            producer.send(masked_topic, masked.value)
            logging.info('Consumer: Sending results data to "%s"...', result_topic)
            producer.send(result_topic, results.value)
            logging.info('Consumer: Messages sent.')


def produce_events():
    logging.info('Started producer.')
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
    with open('message.json', 'rb') as f:
        message = f.read()

    while True:
        producer.send(source_topic, message)
        logging.info('Producer: Sent message.')
        time.sleep(3)


if __name__ == "__main__":
    logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.INFO)

    session = requests.Session()
    try:
        setup(session)
        consumer = Process(target=consume_events, args=[session], name="ConsumerThread")
        consumer.start()

        producer = Process(target=produce_events, name='ProducerThread')
        producer.start()


        # Graceful handling of ctrl-C termination.
        def terminate_processes(*args):
            consumer.terminate()
            producer.terminate()


        signal.signal(signal.SIGINT, terminate_processes)
        signal.signal(signal.SIGTERM, terminate_processes)

        producer.join()  # Freeze thread until the producer process is terminated.
    finally:
        teardown(session)
