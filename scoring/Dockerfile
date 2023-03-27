FROM python:3.9-slim-buster
RUN apt update && apt install tzdata -y
ENV TZ="Asia/Jakarta"
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY . /app
WORKDIR /app
