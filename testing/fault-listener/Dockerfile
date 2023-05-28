FROM python:3.10-slim-buster

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 8000

CMD ["python", "fault_listener.py"]
