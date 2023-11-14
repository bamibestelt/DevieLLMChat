import json
import time

import pika

from constants import UPDATE_STATUS_QUEUE, RABBIT_HOST, BLOG_RSS
from persistence import persist_documents
from processors.rss_processor import parse_blog_document, parse_rss_link
from utils import LLMStatusCode

is_updating_data = False
current_update_status = LLMStatusCode.IDLE


# send
def publish_message(message: str, queue: str):
    bytes_msg = message.encode('utf-8')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_publish(exchange='', routing_key=queue, body=bytes_msg)
    print(f"message {message} is sent to {queue}")
    channel.close()
    connection.close()


# set to listen queue
def consume_message(target_queue: str, target_callback: ()):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=target_queue)
    channel.basic_consume(queue=target_queue, on_message_callback=target_callback, auto_ack=True)
    channel.start_consuming()


# receiver of queue: BLOG_REQUEST_QUEUE
def listen_to_request_queue(channel, method, properties, body):
    global current_update_status
    global is_updating_data

    if is_updating_data:
        print("llm engine is still busy persisting data")
        publish_message(current_update_status, UPDATE_STATUS_QUEUE)
    
    is_updating_data = True
    print("start updating data")

    update_current_status(LLMStatusCode.START)
    rss_link = body.decode('utf-8')

    update_current_status(LLMStatusCode.GET_RSS)
    links = parse_rss_link(BLOG_RSS)
    
    update_current_status(LLMStatusCode.PARSING)
    docs = parse_blog_document(links)

    update_current_status(LLMStatusCode.SAVING)
    persist_documents(docs)

    update_current_status(LLMStatusCode.FINISH)

    is_updating_data = False


def update_current_status(status: LLMStatusCode):
    current_update_status = f"{status.value}"
    publish_message(current_update_status, UPDATE_STATUS_QUEUE)
