import json
import threading
import time

import pika
from fastapi.encoders import jsonable_encoder

from constants import RABBIT_HOST, BLOG_RSS, BLOG_LINKS_REQUEST, BLOG_LINKS_REPLY
from persistence import persist_documents
from utils import parse_blog_document, LLMStatusCode, get_llm_status

is_updating_data = False
current_update_status = LLMStatusCode.IDLE
previous_update_status = LLMStatusCode.IDLE


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


def provide_status_stream():
    print(f"UpdateStatusAsyncStream: starts")
    global current_update_status
    global previous_update_status
    streaming_active = True

    while streaming_active:
        if current_update_status != previous_update_status:
            if (current_update_status == LLMStatusCode.IDLE and
                    previous_update_status != LLMStatusCode.IDLE):
                # we reach the stop condition for the iterator
                print(f"UpdateStatusAsyncStream: ends")
                yield "event: end\n\n"
                previous_update_status = LLMStatusCode.IDLE
                streaming_active = False
            else:
                # return the updated status
                previous_update_status = current_update_status
                print(f"UpdateStatusAsyncStream: {current_update_status}")
                yield f"event: data\ndata: {json.dumps(jsonable_encoder(get_llm_status(current_update_status)))}\n\n"
                if current_update_status == LLMStatusCode.FINISH:
                    normalize_update_status()
        else:
            yield f"event: data\ndata: {json.dumps(jsonable_encoder(get_llm_status(current_update_status)))}\n\n"
        time.sleep(1)


def normalize_update_status():
    time.sleep(3)
    global current_update_status
    current_update_status = LLMStatusCode.IDLE


def start_data_update_request():
    global current_update_status
    global is_updating_data
    if is_updating_data:
        print("llm engine is still busy persisting data")
        return provide_status_stream()
    print("start updating data")
    is_updating_data = True
    current_update_status = LLMStatusCode.START
    blog_links_thread = threading.Thread(target=start_links_request)
    blog_links_thread.start()


# send data update status to client
# send data request to blog rss processor
# listening to reply
def start_links_request():
    global current_update_status
    current_update_status = LLMStatusCode.GET_RSS
    publish_message(BLOG_RSS, BLOG_LINKS_REQUEST)
    print('Listening to blog processor reply...')
    consume_message(BLOG_LINKS_REPLY, links_receiver)


def links_receiver(channel, method, properties, body):
    global current_update_status
    print(f"Received processor: {channel}")
    bytes_to_string = body.decode('utf-8')
    links = json.loads(bytes_to_string)
    print(f"Links data received: {len(links)}")
    channel.stop_consuming()

    current_update_status = LLMStatusCode.PARSING
    docs = parse_blog_document(links)

    current_update_status = LLMStatusCode.SAVING
    persist_documents(docs)

    current_update_status = LLMStatusCode.FINISH

    global is_updating_data
    is_updating_data = False
