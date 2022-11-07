# syntax=docker/dockerfile:1
FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY . /app/
WORKDIR /app/blogpost-project
RUN pip install --upgrade pip
RUN pip install -r ../requirements.txt