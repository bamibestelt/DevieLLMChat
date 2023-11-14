import argparse

from constants import BLOG_RSS
from rabbit import start_data_update_request


def main():
    print("RSS processor starting...")
    args = parse_arguments()
    if args.t:
        print("decoding from hard coded rss path")
        start_data_update_request()
        return
    start_data_update_request()


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
