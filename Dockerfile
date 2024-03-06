# Top level build args
ARG build_for=linux/amd64

##
# base image (abstract)
##
FROM --platform=$build_for python:3.10.7-slim-bullseye as base

# N.B. The refs updated automagically every release via bumpversion
ARG dbt_core_ref=dbt-core@v1.8.0b1
ARG dbt_bigquery_ref=dbt-bigquery@v1.8.0b1

# System setup
RUN apt-get update \
  && apt-get dist-upgrade -y \
  && apt-get install -y --no-install-recommends \
    git \
    ssh-client \
    software-properties-common \
    make \
    build-essential \
    ca-certificates \
    libpq-dev \
  && apt-get clean \
  && rm -rf \
    /var/lib/apt/lists/* \
    /tmp/* \
    /var/tmp/*

# Env vars
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

# Update python
RUN python -m pip install --upgrade pip setuptools wheel --no-cache-dir

##
# dbt-core
##
FROM base as dbt-core
ARG dbt_core_ref
RUN python -m pip install --no-cache-dir "git+https://github.com/dbt-labs/${dbt_core_ref}#egg=dbt-core&subdirectory=core"

##
# dbt-bigquery
##
FROM base as dbt-bigquery
ARG dbt_bigquery_ref
RUN python -m pip install --no-cache-dir "git+https://github.com/dbt-labs/${dbt_bigquery_ref}#egg=dbt-bigquery"


FROM mageai/mageai:latest

ARG PIP=pip3
ARG USER_CODE_PATH=/home/src/${PROJECT_NAME}


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

# Set up dbt
RUN ${PIP} install dbt

ENV MAGE_DATA_DIR=

