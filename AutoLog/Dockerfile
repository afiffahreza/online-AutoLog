FROM python:3.10-slim-buster

RUN apt update && apt install tzdata -y && apt install curl -y && apt install unzip -y
ENV TZ="Asia/Jakarta"

RUN curl -O -L "https://github.com/grafana/loki/releases/download/v2.7.5/logcli-linux-amd64.zip"
RUN unzip "logcli-linux-amd64.zip"
RUN chmod a+x "logcli-linux-amd64"
RUN mv "logcli-linux-amd64" "/usr/local/bin/logcli"
RUN logcli --version

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY . /app
WORKDIR /app
RUN mkdir output

CMD ["python3", "main.py"]
