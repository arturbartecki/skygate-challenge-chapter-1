FROM python:3.7-alpine
MAINTAINER Artur Bartecki

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /src
WORKDIR /src
COPY ./src /src

RUN python manage.py migrate
RUN python manage.py loaddata basefixture.json

RUN adduser -D user
USER user
