FROM python:3.11-slim-bookworm

# Keep non-interactive during apt installs
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    # Add sudo, potentially needed by dev container features/scripts later
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# --- FIX: Add the CORRECT path reported by the uv installer ---
ENV PATH="/root/.local/bin:${PATH}"
# Verify uv installation using the updated PATH
RUN uv --version

# Install Pulumi
# Use a standard location
ENV PULUMI_HOME="/usr/local/pulumi"
# Install Pulumi without modifying user profile paths directly
# The '-s -- --no-modify-path' tells the script not to mess with .bashrc etc.
RUN curl -fsSL https://get.pulumi.com | sh -s -- --no-modify-path
# Add Pulumi's bin to the system PATH
ENV PATH="${PULUMI_HOME}/bin:${PATH}"
# Verify Pulumi installation
RUN pulumi version

# Install Dagger CLI into a standard location
RUN curl -L https://dl.dagger.io/dagger/install.sh | BIN_DIR=/usr/local/bin sh
# Verify Dagger installation
RUN dagger version

# Switch back to dialog for interactive shells if needed later (optional)
ENV DEBIAN_FRONTEND=dialog