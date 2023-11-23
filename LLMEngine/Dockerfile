# Use the latest version of Ubuntu as a parent image
FROM python:3.11.4

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

COPY template.env /app/.env

# upgrade pip
RUN pip3 install --upgrade pip

# install everything in requirements.txt except gpt4all which has problem
RUN pip3 install --no-cache-dir -r requirements.txt

# rss blog links channel
ENV MODEL_PATH=""
ENV MODEL_TYPE="LlamaCpp"
ENV OPENAI_API_KEY=""
ENV CHROMA_HOST="localhost"
ENV CHROMA_PORT=""
ENV RABBIT_HOST="localhost"
ENV RABBIT_USER=""
ENV RABBIT_PASS=""

EXPOSE 8080

# Run main.py when the container launches
CMD ["python", "main.py"]