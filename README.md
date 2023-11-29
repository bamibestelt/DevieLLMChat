# DeviesLLMChat!
## Introduction
This integration consists of:
1. **LLMPersistence**: contains processor modules to process data from website, api, webscraping etc and persist them into the vector database.
2. **LLMEngine**: receive http requests of prompts, contains logic to create and utilize LLM to respond to the prompt.
3. **Chat Client**: the UI interface where user can chat with the LLMEngine. 


## How to use
1. Download **devies-llm-chat.tar.gz** from the Release.
2. Download **.env** file from **DeviesLLMChat** section in **1Password** and put it inside **LLMEngine** folder.
3. You can use llm file to run the app locally for free. Download the llm file from [GPT4All website](https://gpt4all.io/index.html) then copy the llm file into **./LLMEngine/models**. My recommendation is **mistral-7b-instruct** or **nous-hermes**. You can also use your **OpenAI** API key to communicate with an OpenAI backend.
4. Get inside the **executable** folder and run the run.sh file. It will try to install all the dependencies for the first time.


## Components
### CodaProcessor

    pip install playwright
    playwright install

### LLMPersistence
    build dockerfile
    docker buildx build --platform linux/amd64 -t llm-persistence .

**run llm-persistence:**
required: rabbitmq chromadb

    docker run --net=host --restart unless-stopped -d llm-persistence

**environment variables to set:**

    ENV CHROMA_HOST=""
    ENV CHROMA_PORT=""
    ENV RABBIT_HOST=""
    ENV RABBIT_USER=""
    ENV RABBIT_PASS=""


### LLMEngine
contains logic to communicate with retriever and llm. You can choose to run it locally on you machine or use OpenAI. Details about the parameters can be seen in **DeviesLLMChat Compose** in **1Password**.

docker run -p 8080:8080 -e OPENAI_API_KEY=sk-xxxx --restart unless-stopped -d bamibestelt/llm-engine


### ChatGPT-Client-Web
The frontend chat client. All he knows is to communicate with the LLMEngine
setup:

    sudo apt-get remove nodejs
    sudo apt-get update
    sudo apt-get autoremove
    curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
    source ~/.profile
    nvm install 16.15.1
    run with: yarn dev.

docker run -p 3000:3000 --restart unless-stopped -d devies-llm-chat

## TODOs:
1. Implement document processor for Google Drive.
2. Implement document processor for Tools.
3. Implement document processor and web scraping for Coda docs.


## References
https://github.com/imartinez/privateGPT
https://github.com/langchain-ai/langchain
https://github.com/nomic-ai/gpt4all
https://github.com/Yidadaa/ChatGPT-Next-Web


