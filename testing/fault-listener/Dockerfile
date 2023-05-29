FROM python:3.10-slim-buster

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "fault_listener:app", "-k", "uvicorn.workers.UvicornWorker"]
