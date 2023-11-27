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
ENV MODEL_TYPE="OpenAI"
ENV OPENAI_API_KEY=""

EXPOSE 8080

# Run main.py when the container launches
CMD ["python", "main.py"]