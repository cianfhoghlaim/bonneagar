FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN uv --version

ENV PULUMI_HOME="/usr/local/pulumi"
RUN curl -fsSL https://get.pulumi.com | sh -s -- --no-modify-path
ENV PATH="${PULUMI_HOME}/bin:${PATH}"
RUN pulumi version

RUN cd /usr/local && curl -L https://dl.dagger.io/dagger/install.sh | BIN_DIR=/usr/local/bin sh
RUN dagger version

ENV DEBIAN_FRONTEND=dialog