FROM python:3.9.6-slim-buster


# Pypi package Repo upgrade
RUN apt-get install -y ffmpeg python3-pip curl
RUN apt-get update && apt-get install libgl1
RUN pip3 install --upgrade pip setuptools
ENV PATH="/home/bot/bin:$PATH"

# make directory
RUN mkdir /MissCutie/
COPY . /MissCutie
WORKDIR /MissCutie

# Install requirements
RUN pip3 install -U -r requirements.txt

# Starting Worker
CMD ["python3","-m","MissCutie"]
