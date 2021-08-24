# syntax=docker/dockerfile:1
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get upgrade
# Build dependancies
RUN apt-get install python3-dev default-libmysqlclient-dev gcc ffmpeg libsm6 libxext6 -y 
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install djangorestframework
EXPOSE 8000
