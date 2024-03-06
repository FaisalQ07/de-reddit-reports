FROM mageai/mageai:latest

ARG PIP=pip3
ARG USER_CODE_PATH=/home/src/${PROJECT_NAME}


# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    curl \
    git \
    ssh-client \
    software-properties-common \
    make \
    build-essential \
    ca-certificates \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# System setup
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

# Update Python
RUN ${PIP} install --upgrade pip setuptools wheel --no-cache-dir

# Install dbt dependencies
RUN ${PIP} install --no-cache-dir \
    dbt-core==1.0.1 \
    dbt-postgres==1.0.1 \
    dbt-bigquery==1.0.0

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

