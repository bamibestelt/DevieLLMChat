import os

from chromadb.config import Settings
from dotenv import load_dotenv

if not load_dotenv():
    print("Could not load .env file or it is empty. Please check if it exists and is readable.")
    exit(1)

# RabbitMQ settings
RABBIT_HOST = os.environ.get('RABBIT_HOST')
UPDATE_REQUEST_QUEUE = os.environ.get('UPDATE_REQUEST_QUEUE')
UPDATE_STATUS_QUEUE = os.environ.get('UPDATE_STATUS_QUEUE')
BLOG_RSS = os.environ.get('BLOG_RSS')

# Define the folder for storing database
PERSIST_DIRECTORY = os.environ.get('PERSIST_DIRECTORY')
if PERSIST_DIRECTORY is None:
    raise Exception("Please set the PERSIST_DIRECTORY environment variable")

EMBEDDINGS_MODEL_NAME = os.environ.get('EMBEDDINGS_MODEL_NAME')

CHROMA_HOST = os.environ.get('CHROMA_HOST')
CHROMA_PORT = os.environ.get('CHROMA_PORT')

# Define the Chroma settings
CHROMA_SETTINGS = Settings(
    chroma_db_impl="duckdb+parquet",
    anonymized_telemetry=False
)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50