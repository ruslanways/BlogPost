# syntax=docker/dockerfile:1
FROM python:3
WORKDIR /app
COPY . /app/
RUN pip install -r requirements.txt