DeviesLLMChat.
A prototype of LLM integration with company data.

This integration consists of 4 layers:
1. Processors: focus on gathering data from various outside sources such as blogs, links, google drive, api endpoints etc. Processors will send data to Persistence component.
2. Persistence: focus on receiving data from processors and persist them into the vector database.
2. LLM: contains api endppoints that will be requested by frontend clients. Have direct connection to LLM binary and required higher than average computing resources.
4. Frontend: UI interface in which user interacts with the system through prompts, commands and data. 

Links for references:
https://github.com/imartinez/privateGPT
https://github.com/langchain-ai/langchain
https://github.com/nomic-ai/gpt4all
https://github.com/Yidadaa/ChatGPT-Next-Web


Components:

CodaProcessor
pip install playwright
playwright install


LLMPersistence
build dockerfile
docker buildx build --platform linux/amd64 -t llm-persistence .
to run llm-persistence
required image: rabbitmq chromadb
docker run --net=host --restart unless-stopped -d llm-persistence
environment variables to set:
ENV CHROMA_HOST=""
ENV CHROMA_PORT=""
ENV RABBIT_HOST=""
ENV RABBIT_USER=""
ENV RABBIT_PASS=""


LLMEngine
contains logic to communicate with retriever and llm. You can choose to run it locally on you machine or use openai. Details about the parameters can be seen in "DeviesLLMChat Compose" in 1Password.

ChatGPT-Client-Web
The frontend chat client. All he knows is to communicate with LLMEngine
setup:
sudo apt-get remove nodejs
sudo apt-get update
sudo apt-get autoremove
curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
source ~/.profile
nvm install 16.15.1
run with: yarn dev.


TODOs:
1. Implement document processor for Google Drive.
2. Implement document processor for Tools.
3. Implement document processor and web scraping for Coda docs.

Tests:
1. Performance.
2. User experience.


