import argparse

from constant import RSS_LINK
from rabbit import start_listen_request_queue, parse_blog_links


def main():
    print("RSS processor starting...")
    args = parse_arguments()
    if args.t:
        print("decoding from hard coded rss path")
        parse_blog_links(RSS_LINK)
        return
    # load RabbitMQ connection
    # listen to message queue
    # use message as rss link
    # reply back with list of url
    start_listen_request_queue()


def parse_arguments():
    parser = argparse.ArgumentParser(description='Run RSS link decoder.')
    parser.add_argument("-t",
                        action='store_true',
                        help='Use this flag to use test links defined in the code.')

    parser.add_argument("-r",
                        action='store_true',
                        help='Use this flag to receive links from RabbitMQ message.')

    return parser.parse_args()


if __name__ == '__main__':
    main()
