FROM python:3.11-slim

ARG API_PORT

COPY mi2gc/ /opt/mi2gc
COPY .env /opt/mi2gc

RUN pip install --no-cache-dir --upgrade -r /opt/mi2gc/requirements.txt

WORKDIR /opt/mi2gc

ENV API_PORT=$API_PORT
