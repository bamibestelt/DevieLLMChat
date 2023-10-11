from constants import LLM_UPDATE_QUEUE
from rabbit import consume_message, data_update_request_receiver, publish_message


def test_data_update_request():
    print('Listening to data-update request...')
    publish_message('test', LLM_UPDATE_QUEUE)
    consume_message(LLM_UPDATE_QUEUE, data_update_request_receiver)
