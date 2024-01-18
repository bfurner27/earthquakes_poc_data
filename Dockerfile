FROM python:3 as base

RUN pip install requests

WORKDIR /app

COPY . app/.

