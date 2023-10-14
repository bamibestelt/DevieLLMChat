import argparse
import json
import time
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.callbacks.tracers.log_stream import RunLogPatch
from langchain.schema.messages import AIMessage, HumanMessage

from privateGPT import get_retriever, create_chain, get_llm
from rabbit import start_data_update_request, provide_status_stream
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


async def transform_stream_for_client(
    stream: AsyncIterator[RunLogPatch],
) -> AsyncIterator[str]:
    async for chunk in stream:
        yield f"event: data\ndata: {json.dumps(jsonable_encoder(chunk))}\n\n"
    yield "event: end\n\n"


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    global trace_url
    trace_url = None
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

    llm = get_llm()
    retriever = get_retriever()
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


def dynamic_data_generator():
    while True:
        # Replace the following line with your dynamic data generation logic
        data = time.ctime()
        yield f'data: {data}\n\n'
        time.sleep(1)


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
            # test_data_update_request()
        return
    else:
        print("live mode started")
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8080)


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
