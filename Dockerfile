FROM python:3.11.4-slim-buster


# Pypi package Repo upgrade
RUN apt-get install -y ffmpeg python3-pip curl
RUN apt update && apt upgrade -y && \
    apt install --no-install-recommends -y \
    libgl1 \
    bzip2 \
    unzip \
    && rm -rf /var/lib/apt/lists /var/cache/apt/archives /tmp




RUN apt install wget
RUN apt-get install ffmpeg -y
RUN apt-get install gifsicle -y
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && apt -fqqy install ./google-chrome-stable_current_amd64.deb && rm google-chrome-stable_current_amd64.deb
RUN wget https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip && unzip chromedriver_linux64.zip && chmod +x chromedriver && mv -f chromedriver /usr/bin/ && rm chromedriver_linux64.zip


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
