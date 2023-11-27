import json
import time

from constants import BLOG_RSS
from persistence import persist_documents
from processors.rss_processor import parse_blog_document, parse_devies_site, parse_rss_link
from utils import LLMStatusCode, get_llm_status, get_status_from_code

is_updating_data = False
current_update_status = LLMStatusCode.IDLE
previous_update_status = LLMStatusCode.IDLE


def start_data_update_request():
    global current_update_status
    global is_updating_data
    if is_updating_data:
        print("llm engine is still busy persisting data")
        return provide_status_stream()
    
    is_updating_data = True
    print("start updating data")

    current_update_status = get_status_from_code(0)
    # rss_link = body.decode('utf-8')
    
    current_update_status = get_status_from_code(1)
    links = parse_rss_link(BLOG_RSS)
    
    current_update_status = get_status_from_code(2)
    docs = parse_blog_document(links)
    docs += parse_devies_site()
    print(f"total docs processed: {len(docs)}")

    current_update_status = get_status_from_code(3)
    try:
        persist_documents(docs)
    except Exception as e:
        print(f"saving documents failed: {e}")

    current_update_status = get_status_from_code(-1)
    is_updating_data = False


def provide_status_stream():
    print(f"UpdateStatusAsyncStream: starts")
    global current_update_status
    global previous_update_status
    global is_updating_data
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
                is_updating_data = False
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

