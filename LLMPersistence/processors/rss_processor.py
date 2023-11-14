from typing import List

import feedparser
from langchain.docstore.document import Document
from langchain.document_loaders import AsyncHtmlLoader


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