FROM python:3.11-alpine3.18

USER root

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV USER=sm_automation
ENV UID=1000
ENV GID=1000

COPY ./requirements.txt .
RUN mkdir /usr/src/app \
    && addgroup -g $GID -S $USER \
    && adduser -u $UID -S $USER -G $USER \
    && apk add libpq bash redis curl postgresql-client   \
    && apk add --no-cache --virtual .build-deps build-base python3-dev gcc musl-dev libffi-dev postgresql-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

WORKDIR /usr/src/app
ADD . .

RUN mkdir -p static \
    && mkdir -p media \
    && chown -R ${USER}:${USER} /usr/src/app/ \
    && chown -R ${USER}:${USER} static \
    && chown -R ${USER}:${USER} media

USER sm_automation
