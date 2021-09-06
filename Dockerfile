# syntax=docker/dockerfile:1
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update -y && apt-get upgrade -y
# Build dependancies
RUN apt-get install python3-dev default-libmysqlclient-dev gcc ffmpeg libsm6 libxext6 -y 
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install djangorestframework
RUN pip install django-cors-headers 
RUN pip install XlsxWriter
RUN pip install Pillow
EXPOSE 8000
