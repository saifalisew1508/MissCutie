FROM python:3.11.4-slim-buster

# Update package lists and upgrade existing packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    bzip2 \
    unzip \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives /tmp/*

# Install gifsicle
RUN apt-get install -y gifsicle

# Download and install Google Chrome
RUN wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i /tmp/google-chrome.deb && \
    apt-get install -y -f && \
    rm /tmp/google-chrome.deb

# Download and install ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -q -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Set the working directory
WORKDIR /MissCutie/

# Copy the local directory contents to the container
COPY . /MissCutie/

# Install Python dependencies
RUN pip3 install --no-cache-dir -U -r requirements.txt

# Starting the application
CMD ["python3", "-m", "MissCutie"]
