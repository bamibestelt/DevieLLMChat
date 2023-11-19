import argparse

from constants import UPDATE_REQUEST_QUEUE
from rabbit import consume_message, listen_to_request_queue


def main():
    print("persistence service starting...")
    args = parse_arguments()
    if args.t:
        print("test with hard coded source")
        # start_data_update_request()
        return
    consume_message(UPDATE_REQUEST_QUEUE, listen_to_request_queue)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Run persistence.')
    parser.add_argument("-t",
                        action='store_true',
                        help='Use this flag to use test links defined in the code.')

    parser.add_argument("-r",
                        action='store_true',
                        help='Use this flag to receive links from RabbitMQ message.')

    return parser.parse_args()


if __name__ == '__main__':
    main()
