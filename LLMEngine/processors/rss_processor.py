from typing import List

import feedparser
from bs4 import BeautifulSoup as Soup
from langchain.docstore.document import Document
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_loaders.recursive_url_loader import RecursiveUrlLoader


def parse_rss_link(rss_path: str) -> List[str]:
    feed = feedparser.parse(rss_path)
    print(f"rss feed entries: {len(feed.entries)}")
    links = []
    for entry in feed.entries:
        links.append(entry.link)
    print(f"total blog links processed: {len(links)}")
    return links


def parse_blog_document(links: List[str]) -> List[Document]:
    loader = AsyncHtmlLoader(links)
    docs = loader.load()
    print("decoding links success")
    return docs


def parse_devies_site() -> List[Document]:
    loader = RecursiveUrlLoader(url="https://www.devies.se/", 
                                max_depth=4, 
                                extractor=lambda x: Soup(x, "html.parser").text)
    docs = loader.load()
    # Check and replace None metadata values
    for doc in docs:
        for key, value in doc.metadata.items():
            if value is None:
                doc.metadata[key] = ""
    print(f"decoding devies website success: {len(docs)}")
    return docs