from enum import Enum
from typing import Dict, List, Optional

from langchain.docstore.document import Document
from langchain.document_loaders import AsyncHtmlLoader
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]]
    conversation_id: Optional[str]


class LLMStatus(BaseModel):
    status_code: int
    status_message: str


class LLMStatusCode(Enum):
    START = 0
    GET_RSS = 1
    PARSING = 2
    SAVING = 3
    FINISH = -1
    IDLE = -2


def get_llm_status_message(code):
    return {
        LLMStatusCode.START: "start",
        LLMStatusCode.GET_RSS: "fetching",
        LLMStatusCode.PARSING: "parsing",
        LLMStatusCode.SAVING: "saving",
        LLMStatusCode.FINISH: "finish",
        LLMStatusCode.IDLE: "idle",
    }.get(code, "unknown")


def get_llm_status(code: LLMStatusCode) -> dict:
    status = dict(
        status_code=code.value,
        status_message=get_llm_status_message(code)
    )
    return status


def get_status_from_code(code):
    return {
        0: LLMStatusCode.START,
        1: LLMStatusCode.GET_RSS,
        2: LLMStatusCode.PARSING,
        3: LLMStatusCode.SAVING,
        -1: LLMStatusCode.FINISH,
        -2: LLMStatusCode.IDLE,
    }.get(code, LLMStatusCode.IDLE)


REPHRASE_TEMPLATE = """\
Given the following conversation and a follow up question, rephrase the follow up \
question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone Question:"""
