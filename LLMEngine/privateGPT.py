from operator import itemgetter
from typing import Sequence

import chromadb
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import GPT4All, LlamaCpp
from langchain.prompts import (ChatPromptTemplate, MessagesPlaceholder,
                               PromptTemplate)
from langchain.schema import Document
from langchain.schema.language_model import BaseLanguageModel
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.retriever import BaseRetriever
from langchain.schema.runnable import Runnable, RunnableMap
from langchain.vectorstores import Chroma

from constants import CHROMA_SETTINGS, EMBEDDINGS_MODEL_NAME, PERSIST_DIRECTORY, TARGET_SOURCE_CHUNKS, MODEL_TYPE, \
    MODEL_N_BATCH, MODEL_N_CTX, MODEL_PATH
from utils import REPHRASE_TEMPLATE, RESPONSE_TEMPLATE


def get_retriever() -> BaseRetriever:
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL_NAME)
    print('embeddings obtained...')

    chroma_client = chromadb.PersistentClient(settings=CHROMA_SETTINGS, path=PERSIST_DIRECTORY)
    db = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings, client_settings=CHROMA_SETTINGS,
                client=chroma_client)
    print('chromadb client obtained...')
    retriever = db.as_retriever(search_kwargs={"k": TARGET_SOURCE_CHUNKS})
    print('vector store retriever obtained...')
    return retriever


def create_retriever_chain(
    llm: BaseLanguageModel, retriever: BaseRetriever, use_chat_history: bool
) -> Runnable:
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(REPHRASE_TEMPLATE)
    if not use_chat_history:
        initial_chain = (itemgetter("question")) | retriever
        return initial_chain
    else:
        condense_question_chain = (
            {
                "question": itemgetter("question"),
                "chat_history": itemgetter("chat_history"),
            }
            | CONDENSE_QUESTION_PROMPT
            | llm
            | StrOutputParser()
        ).with_config(
            run_name="CondenseQuestion",
        )
        conversation_chain = condense_question_chain | retriever
        return conversation_chain


def format_docs(docs: Sequence[Document]) -> str:
    formatted_docs = []
    for i, doc in enumerate(docs):
        doc_string = f"<doc id='{i}'>{doc.page_content}</doc>"
        formatted_docs.append(doc_string)
    return "\n".join(formatted_docs)


def create_chain(
    llm: BaseLanguageModel,
    retriever: BaseRetriever,
    use_chat_history: bool = False,
) -> Runnable:
    retriever_chain = create_retriever_chain(
        llm, retriever, use_chat_history
    ).with_config(run_name="FindDocs")
    _context = RunnableMap(
        {
            "context": retriever_chain | format_docs,
            "question": itemgetter("question"),
            "chat_history": itemgetter("chat_history"),
        }
    ).with_config(run_name="RetrieveDocs")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", RESPONSE_TEMPLATE),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    response_synthesizer = (prompt | llm | StrOutputParser()).with_config(
        run_name="GenerateResponse",
    )
    return _context | response_synthesizer


def get_llm() -> BaseLanguageModel:
    global llm
    llm = None
    match MODEL_TYPE:
        case "LlamaCpp":
            llm = LlamaCpp(model_path=MODEL_PATH,
                           max_tokens=MODEL_N_CTX,
                           n_batch=MODEL_N_BATCH,
                           callbacks=[],
                           verbose=False)
        case "GPT4All":
            llm = GPT4All(model=MODEL_PATH,
                          max_tokens=MODEL_N_CTX,
                          backend='gptj',
                          n_batch=MODEL_N_BATCH,
                          callbacks=[],
                          verbose=False)
    return llm
