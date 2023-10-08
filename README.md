DeviesLLMChat.
A prototype of LLM integration with company data.

This integration consists of 4 layers:
1. Processors: gathers data from outside source such as blogs, links, google drive, api endpoints etc. (may need to move langchain document transformation here in the processors instead of in the LLM layer).
2. LLM: receive data from processors, turn them into documents, persist them into vector database and allows them to be queried with prompts.
3. API service: manages communication with the front-end and translate them into commands and requests to LLM layer.
4. Frontend: UI interface in which user interacts with the system through prompts, commands and data. 



Components:

RSSProcessor
to run rss-processor
docker run -d --net=host rss-processor

environment variables to set:
ENV RABBIT_HOST="localhost"
ENV RSS_LINK=""


LLMEngine
build docker image with platform flag.
docker buildx build --platform linux/amd64 -t llm-engine .

run docker image with platform flag.
docker run --platform linux/amd64 llm-engine

environment variables to set:
ENV RABBIT_HOST="localhost"

volumes to set:
ENV PERSIST_DIRECTORY=""
ENV MODEL_PATH=""


LLMCommApi
to run llm-comm-api
docker run -d --net=host -e RabbitMQ_Host=localhost llm-comm-api
to override the appsettings.json.


ChatGPT-Client-Web
run with: yarn dev.
hardcoded parameter:
api base path: https://localhost:7186/llm as stated by LLMCommApi.
original repo: https://github.com/Yidadaa/ChatGPT-Next-Web
Read instruction in <original repo> for setup the project



Notes:
1. docker-compose is not yet tested.


TODOs:
1. Implement document processor for Google Drive.
2. Implement document processor for Tools.
3. Implement document processor and web scraping for Coda docs.
4. Creating new LLM instance for new user session?
5. Chaining LLMs.

Tests:
1. Performance.
2. User experience.


