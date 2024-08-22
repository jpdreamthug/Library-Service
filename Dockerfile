FROM python:3.11.9-alpine3.19

ENV PYTHONUNBUFFERED 1
ENV DOCKER 1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY . .