FROM mageai/mageai:latest

ARG PIP=pip3
ARG USER_CODE_PATH=/home/src/${PROJECT_NAME}


# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Download the Google Cloud SDK archive
RUN curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-466.0.0-linux-x86_64.tar.gz

# Extract the archive to the home directory
RUN tar -xf google-cloud-cli-466.0.0-linux-x86_64.tar.gz -C /usr/local/

# Run the installation script
RUN /usr/local/google-cloud-sdk/install.sh

# Add gcloud CLI to the PATH
ENV PATH="/usr/local/google-cloud-sdk/bin:${PATH}"

# Install Python dependencies
COPY requirements.txt ${USER_CODE_PATH}requirements.txt
RUN ${PIP} install -r ${USER_CODE_PATH}requirements.txt

ENV MAGE_DATA_DIR=

