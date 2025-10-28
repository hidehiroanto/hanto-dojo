# syntax=docker/dockerfile:labs

FROM python:alpine

RUN pip install --no-cache-dir pyyaml

ADD --chmod=6755 http://github.com/pwncollege/exec-suid/releases/latest/download/exec-suid /usr/bin/

RUN ln -s /usr/local/bin/python /usr/bin/python \
    && ln -s /usr/local/bin/python3 /usr/bin/python3
