FROM python:3.11-slim-bookworm

# Keep non-interactive during apt installs
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# Add uv's actual install location (from logs) to the system PATH
ENV PATH="/root/.local/bin:${PATH}"
# Verify uv installation
RUN uv --version

# Install Pulumi
# The installer script defaults to ~/.pulumi/bin (which is /root/.pulumi/bin here)
# The --no-modify-path flag prevents it changing shell config files.
RUN curl -fsSL https://get.pulumi.com | sh -s -- --no-modify-path
# --- FIX: Add the ACTUAL install path reported by the installer ---
ENV PATH="/root/.pulumi/bin:${PATH}"
# Verify Pulumi installation using the updated PATH
RUN pulumi version

# Install Dagger CLI into a standard location
RUN curl -L https://dl.dagger.io/dagger/install.sh | BIN_DIR=/usr/local/bin sh
# Verify Dagger installation
RUN dagger version

# Switch back to dialog for interactive shells if needed later (optional)
ENV DEBIAN_FRONTEND=dialog