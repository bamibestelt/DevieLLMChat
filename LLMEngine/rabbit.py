import json
import threading

import pika

from constants import RABBIT_HOST, LLM_UPDATE_QUEUE, LLM_STATUS_QUEUE, BLOG_RSS, BLOG_LINKS_REQUEST, BLOG_LINKS_REPLY
from persistence import persist_documents
from utils import parse_blog_document, LLMStatusCode, get_llm_status

is_updating_data = False


def publish_message(message: str, queue: str):
    bytes_msg = message.encode('utf-8')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_publish(exchange='', routing_key=queue, body=bytes_msg)
    print(f"message {message} is sent to {queue}")
    channel.close()
    connection.close()


def consume_message(target_queue: str, target_callback: ()):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=target_queue)
    channel.basic_consume(queue=target_queue, on_message_callback=target_callback, auto_ack=True)
    channel.start_consuming()


def start_listen_data_update_request():
    print('Listening to data-update request...')
    consume_message(LLM_UPDATE_QUEUE, data_update_request_receiver)


def data_update_request_receiver(channel, method, properties, body):
    global is_updating_data
    if is_updating_data:
        print("llm engine is still busy persisting data")
        return

    is_updating_data = True
    request = body.decode('utf-8')
    print(f"data-update request: {request}")
    publish_message(get_llm_status(LLMStatusCode.START), LLM_STATUS_QUEUE)
    blog_links_thread = threading.Thread(target=start_links_request)
    blog_links_thread.start()
    blog_links_thread.join()


# send data update status to client
# send data request to blog rss processor
# listening to reply
def start_links_request():
    publish_message(get_llm_status(LLMStatusCode.GET_RSS), LLM_STATUS_QUEUE)
    publish_message(BLOG_RSS, BLOG_LINKS_REQUEST)
    print('Listening to blog processor reply...')
    consume_message(BLOG_LINKS_REPLY, links_receiver)


def links_receiver(channel, method, properties, body):
    print(f"Received processor: {channel}")
    bytes_to_string = body.decode('utf-8')
    links = json.loads(bytes_to_string)
    print(f"Links data received: {len(links)}")
    channel.stop_consuming()

    publish_message(get_llm_status(LLMStatusCode.PARSING), LLM_STATUS_QUEUE)
    docs = parse_blog_document(links)

    publish_message(get_llm_status(LLMStatusCode.SAVING), LLM_STATUS_QUEUE)
    persist_documents(docs)

    publish_message(get_llm_status(LLMStatusCode.FINISH), LLM_STATUS_QUEUE)

    global is_updating_data
    is_updating_data = False

