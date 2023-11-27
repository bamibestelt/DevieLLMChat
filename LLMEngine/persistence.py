from typing import List

import chromadb
from chromadb.api.segment import API
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

from constants import PERSIST_DIRECTORY, CHROMA_SETTINGS, EMBEDDINGS_MODEL_NAME, CHUNK_SIZE, CHUNK_OVERLAP


def does_vectorstore_exist(embeddings: HuggingFaceEmbeddings) -> bool:
    """
    Checks if vectorstore exists
    """
    db = Chroma(persist_directory=PERSIST_DIRECTORY, 
                embedding_function=embeddings)
    if not db.get()['documents']:
        return False
    return True


def process_documents(documents: List[Document], ignored_files: List[str] = []) -> List[Document]:
    """
    Load documents and split in chunks
    """
    print(f"persistence. total docs: {len(documents)}")
    # print(f"persistence. ignored files: {ignored_files}")
    docs = [doc for doc in documents if doc.metadata['source'] not in ignored_files]
    print(f"persistence. docs to be saved: {len(docs)}")
    if not docs:
        print("No new documents to load")
        return docs
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    documents = text_splitter.split_documents(documents)
    print(f"Split into {len(documents)} chunks of text (max. {CHUNK_SIZE} tokens each)")
    return documents


def batch_chromadb_insertions(chroma_client: API, documents: List[Document]) -> List[Document]:
    """
    Split the total documents to be inserted into batches of documents that the local chroma client can process
    """
    # Get max batch size.
    max_batch_size = chroma_client.max_batch_size
    for i in range(0, len(documents), max_batch_size):
        yield documents[i:i + max_batch_size]


def persist_documents(texts: List[Document]):
    # Create embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL_NAME)
    # Chroma client
    chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)

    if does_vectorstore_exist(embeddings):
        # Update and store locally vectorstore
        print(f"Appending to existing vectorstore at localhost")
        db = Chroma(persist_directory=PERSIST_DIRECTORY,
                    client_settings=CHROMA_SETTINGS,
                    embedding_function=embeddings,
                    client=chroma_client)
        print(f"Creating embeddings. May take some minutes...")
        collection = db.get()
        documents = process_documents(texts, [metadata['source'] for metadata in collection['metadatas']])

        if documents:
            print(f"Creating embeddings. May take some minutes...")
            for batched_chromadb_insertion in batch_chromadb_insertions(chroma_client, documents):
                db.add_documents(batched_chromadb_insertion)
    else:
        # Create and store locally vectorstore
        print("Creating new vectorstore")
        documents = process_documents(texts)
        print(f"Creating embeddings. May take some minutes...")
        batched_chromadb_insertions = batch_chromadb_insertions(chroma_client, documents)
        first_insertion = next(batched_chromadb_insertions)
        db = Chroma.from_documents(documents=first_insertion, 
                                   embedding=embeddings,
                                   persist_directory=PERSIST_DIRECTORY,
                                   client_settings=CHROMA_SETTINGS,
                                   client=chroma_client)
        # Add the rest of batches of documents
        for batched_chromadb_insertion in batched_chromadb_insertions:
            db.add_documents(batched_chromadb_insertion)

    print(f"Ingestion complete! You can now run GPT to query your documents")
