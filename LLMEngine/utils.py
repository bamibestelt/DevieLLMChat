from typing import List
from langchain.docstore.document import Document
from langchain.document_loaders import AsyncHtmlLoader


def parse_blog_document(links: List[str]) -> List[Document]:
    loader = AsyncHtmlLoader(links)
    docs = loader.load()
    print("decoding links success")
    return docs
