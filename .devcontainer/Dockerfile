FROM python:3.11-slim-bookworm

# Keep non-interactive during apt installs
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    # Add sudo, needed by some dev container features/scripts
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# Add uv's default install location (for root) to the system PATH
# This ensures it's available later for the non-root vscode user
ENV PATH="/root/.cargo/bin:${PATH}"
# Verify uv installation using the updated PATH
RUN uv --version

# Install Pulumi
# Use a standard location like /usr/local/pulumi instead of root's home
ENV PULUMI_HOME="/usr/local/pulumi"
# Install Pulumi without modifying user profile paths directly
RUN curl -fsSL https://get.pulumi.com | sh -s -- --no-modify-path
# Add Pulumi's bin to the system PATH
ENV PATH="${PULUMI_HOME}/bin:${PATH}"
# Verify Pulumi installation
RUN pulumi version

# Install Dagger CLI into a standard location
# The BIN_DIR=/usr/local/bin should make it available system-wide
RUN curl -L https://dl.dagger.io/dagger/install.sh | BIN_DIR=/usr/local/bin sh
# Verify Dagger installation
RUN dagger version

# Switch back to dialog for interactive shells if needed later (though devcontainer usually non-interactive)
ENV DEBIAN_FRONTEND=dialog