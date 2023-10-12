from enum import Enum
from typing import List
from langchain.docstore.document import Document
from langchain.document_loaders import AsyncHtmlLoader
from pydantic import BaseModel


class LLMStatus(BaseModel):
    status_code: int
    status_message: str


class LLMStatusCode(Enum):
    START = 0
    GET_RSS = 1
    PARSING = 2
    SAVING = 3
    FINISH = -1


def get_llm_status_message(code):
    return {
        LLMStatusCode.START: "start",
        LLMStatusCode.GET_RSS: "fetching",
        LLMStatusCode.PARSING: "parsing",
        LLMStatusCode.SAVING: "saving",
        LLMStatusCode.FINISH: "finish",
    }.get(code, "unknown")


def get_llm_status(code: LLMStatusCode) -> str:
    status = LLMStatus(
        status_code=code.value,
        status_message=get_llm_status_message(code)
    )
    return status.json()


def parse_blog_document(links: List[str]) -> List[Document]:
    loader = AsyncHtmlLoader(links)
    docs = loader.load()
    print("decoding links success")
    return docs
