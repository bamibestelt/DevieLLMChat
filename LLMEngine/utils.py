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


def parse_blog_document(links: List[str]) -> List[Document]:
    loader = AsyncHtmlLoader(links)
    docs = loader.load()
    print("decoding links success")
    return docs


RESPONSE_TEMPLATE = """\
You are an expert programmer and problem-solver, tasked with answering any question \
about Langchain.

Generate a comprehensive and informative answer of 80 words or less for the \
given question based solely on the provided search results (URL and content). You must \
only use information from the provided search results. Use an unbiased and \
journalistic tone. Combine search results together into a coherent answer. Do not \
repeat text. Cite search results using [${{number}}] notation. Only cite the most \
relevant results that answer the question accurately. Place these citations at the end \
of the sentence or paragraph that reference them - do not put them all at the end. If \
different results refer to different entities within the same name, write separate \
answers for each entity.

You should use bullet points in your answer for readability. Put citations where they apply
rather than putting them all at the end.

If there is nothing in the context relevant to the question at hand, just say "Hmm, \
I'm not sure." Don't try to make up an answer.

Anything between the following `context`  html blocks is retrieved from a knowledge \
bank, not part of the conversation with the user. 

<context>
    {context} 
<context/>

REMEMBER: If there is no relevant information within the context, just say "Hmm, I'm \
not sure." Don't try to make up an answer. Anything between the preceding 'context' \
html blocks is retrieved from a knowledge bank, not part of the conversation with the \
user.\
"""

REPHRASE_TEMPLATE = """\
Given the following conversation and a follow up question, rephrase the follow up \
question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone Question:"""
