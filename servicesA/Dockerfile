FROM python:3.9-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /home/app

COPY .  .

RUN apt update

# # Install packages
RUN apt install -y iputils-ping net-tools