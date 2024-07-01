ARG VERSION_PYTHON="3.10.6-slim-buster"

FROM python:${VERSION_PYTHON}

ENV PYTHONUTNBUFFERED 1

LABEL verion="1.0.0" \
    team="devops"

RUN apt-get update -y && apt-get install -y python3-dev gcc \
    build-essential pipenv locales locales-all default-mysql-client vim \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

VOLUME [ "/var/log" ]

COPY Pipfile* ./

RUN set -ex && pipenv install --deploy --system

COPY . /app

RUN useradd admin -s /bin/bash

RUN chown admin:admin /app

USER  admin

CMD [ "/usr/local/bin/python3", "-u", "/app/mariadb-backup.py" ]