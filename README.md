DeviesLLMChat.
A prototype of LLM integration with company data.

This integration consists of 4 layers:
1. Processors: gathers data from outside source such as blogs, links, google drive, api endpoints etc. (may need to move langchain document transformation here in the processors instead of in the LLM layer).
2. LLM: receive data from processors, turn them into documents, persist them into vector database and allows them to be queried with prompts.
3. API service: manages communication with the front-end and translate them into commands and requests to LLM layer.
4. Frontend: UI interface in which user interacts with the system through prompts, commands and data. 

Links for references:
https://github.com/imartinez/privateGPT
https://github.com/langchain-ai/langchain
https://github.com/nomic-ai/gpt4all
https://github.com/Yidadaa/ChatGPT-Next-Web


Components:

RSSProcessor
build dockerfile
docker buildx build --platform linux/amd64 -t rss-processor .
to run rss-processor
docker run -d --net=host rss-processor

environment variables to set:
ENV RABBIT_HOST="localhost"
ENV RSS_LINK="https://deviesdevelopment.github.io/blog/posts/index.xml"


LLMEngine
build docker image with platform flag.
docker buildx build --platform linux/amd64 -t llm-engine .

run docker image with platform flag.
docker run -p 8080:8080 --platform linux/amd64 --volume <host_folder>:<container_folder> --env MODEL_TYPE=GPT4All --env PERSIST_DIRECTORY=<container_folder>/db --env MODEL_PATH=<container_folder>/models/nous-hermes-13b.ggmlv3.q4_0.bin -d bamibestelt/llm-engine


ChatGPT-Client-Web
run with: yarn dev.
run docker image
docker run -p 3000:3000 --env BASE_API_URL=<remote_host_name> -d chat-devies-blog


push new image
docker tag image-name:tagname username/image-name:tagname
docker push username/image-name:tagname

push a new tag to repo
docker push bamibestelt/devies-llm-integration:tagname
docker login
docker pull username/image-name:tagname


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


