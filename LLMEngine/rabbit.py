import json
import threading
import time

import pika
from constants import BLOG_RSS, RABBIT_HOST, UPDATE_REQUEST_QUEUE, UPDATE_STATUS_QUEUE

from utils import LLMStatusCode, get_llm_status, get_status_from_code

is_updating_data = False
current_update_status = LLMStatusCode.IDLE
previous_update_status = LLMStatusCode.IDLE


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


def start_links_request():
    publish_message(BLOG_RSS, UPDATE_REQUEST_QUEUE)
    print('Listening to persistence status')
    consume_message(UPDATE_STATUS_QUEUE, status_receiver)


def status_receiver(channel, method, properties, body):
    global current_update_status

    status_code = int(body.decode('utf-8'))
    current_update_status = get_status_from_code(status_code)
    print(f"status received: {current_update_status.name}")

    if current_update_status == LLMStatusCode.FINISH:
        channel.stop_consuming()


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
                llm_status = get_llm_status(current_update_status)
                print(f"UpdateStatusAsyncStream: {current_update_status}")
                yield f"event: data\ndata: {json.dumps(llm_status, ensure_ascii=False)}\n\n"
                if current_update_status == LLMStatusCode.FINISH:
                    normalize_update_status()
        else:
            llm_status = get_llm_status(current_update_status)
            yield f"event: data\ndata: {json.dumps(llm_status, ensure_ascii=False)}\n\n"
        time.sleep(1)


def normalize_update_status():
    time.sleep(3)
    global current_update_status
    current_update_status = LLMStatusCode.IDLE

