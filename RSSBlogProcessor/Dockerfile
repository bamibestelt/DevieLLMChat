# Use the latest version of Ubuntu as a parent image
FROM python:3.11.4

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# upgrade pip
RUN pip3 install --upgrade pip

# install everything in requirements.txt except gpt4all which has problem
RUN pip3 install --no-cache-dir -r requirements.txt

ENV RABBIT_HOST="localhost"
ENV BLOG_REQUEST_QUEUE="blog.request"
ENV BLOG_REPLY_QUEUE="blog.links"
ENV RSS_LINK="https://deviesdevelopment.github.io/blog/posts/index.xml"

# Run main.py when the container launches
CMD ["python3", "main.py"]