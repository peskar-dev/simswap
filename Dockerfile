ARG BASE_IMAGE=python:3.10.11-slim-buster

FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04 as cuda

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    git \
    bash \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN apt update -y && apt upgrade -y && \
    apt-get install -y wget build-essential checkinstall  libncursesw5-dev  libssl-dev  libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev && \
    cd /usr/src && \
    wget https://www.python.org/ftp/python/3.10.11/Python-3.10.11.tgz && \
    tar xzf Python-3.10.11.tgz && \
    cd Python-3.10.11 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    update-alternatives --install /usr/bin/python python /usr/local/bin/python3.10 0 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.10 0 && \
    update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.10 0 && \
    update-alternatives --install /usr/bin/pip3 pip3 /usr/local/bin/pip3.10 0 && \
    rm -rf /var/lib/apt/lists/*


FROM ${BASE_IMAGE} as python

WORKDIR /app

RUN apt update -y && \
    apt upgrade -y && \
    apt install curl -y && \
    pip install poetry==1.7.0

COPY poetry* .
COPY pyproject.toml .
COPY faceswap/roop/requirements.txt .
RUN poetry config virtualenvs.create false
RUN poetry install
RUN pip install requirements.txt

COPY ./faceswap/ /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
