import os
from dotenv import load_dotenv

load_dotenv()

RABBIT_HOST = os.environ.get('RABBIT_HOST')
REQUEST_QUEUE = os.environ.get('BLOG_REQUEST_QUEUE')
BLOG_LINKS_QUEUE = os.environ.get('BLOG_REPLY_QUEUE')
RSS_LINK = os.environ.get('RSS_LINK')
