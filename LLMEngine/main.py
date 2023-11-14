import argparse
import json
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.callbacks.tracers.log_stream import RunLogPatch
from langchain.schema.messages import AIMessage, HumanMessage

from constants import LLM_HOST_ADDRESS, LLM_PORT_ADDRESS
from privateGPT import get_retriever, create_chain, get_llm
from rabbit import provide_status_stream, start_data_update_request
from test import test_get_status_from_code
from utils import ChatRequest

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

llm = None
retriever = None
has_initialized_llm = False


async def transform_stream_for_client(
    stream: AsyncIterator[RunLogPatch],
) -> AsyncIterator[str]:
    async for chunk in stream:
        yield f"event: data\ndata: {json.dumps(jsonable_encoder(chunk))}\n\n"
    yield "event: end\n\n"


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    global llm
    global retriever
    global has_initialized_llm
    question = request.message
    chat_history = request.history or []
    converted_chat_history = []
    for message in chat_history:
        if message.get("human") is not None:
            converted_chat_history.append(HumanMessage(content=message["human"]))
        if message.get("ai") is not None:
            converted_chat_history.append(AIMessage(content=message["ai"]))

    metadata = {
        "conversation_id": request.conversation_id,
    }

    if not has_initialized_llm:
        llm = get_llm()
        retriever = get_retriever()
        has_initialized_llm = True
        print('new llm created')

    answer_chain = create_chain(
        llm,
        retriever,
        use_chat_history=bool(converted_chat_history),
    )
    stream = answer_chain.astream_log(
        {
            "question": question,
            "chat_history": converted_chat_history,
        },
        config={"metadata": metadata},
        include_names=["FindDocs"],
    )
    return StreamingResponse(
        transform_stream_for_client(stream),
        headers={"Content-Type": "text/event-stream"},
    )


@app.post("/update")
async def update_endpoint():
    start_data_update_request()
    return StreamingResponse(provide_status_stream(), media_type='text/event-stream')


def start_llm_service():
    args = parse_arguments()
    if args.t:
        print("test mode")
        while True:
            query = input("\nput anything to start test: ")
            if query == "exit":
                break
            if query.strip() == "":
                continue
            test_get_status_from_code()
        return
    else:
        print("live mode started")
        import uvicorn
        uvicorn.run(app, host=LLM_HOST_ADDRESS, port=LLM_PORT_ADDRESS)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Ingest documents.')
    parser.add_argument("-t",
                        action='store_true',
                        help='Use this flag to use test rss defined in the code.')

    parser.add_argument("-r",
                        action='store_true',
                        help='Use this flag to listen to trigger from frontend.')

    return parser.parse_args()


if __name__ == '__main__':
    start_llm_service()
