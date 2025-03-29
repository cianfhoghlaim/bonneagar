# Use an official Python runtime as a parent image
# Using slim-bullseye for a smaller image size, adjust Python version/Debian release if needed
FROM python:3.11-slim-bullseye

# Set environment variables to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive \
    # Define versions (optional, could be ARG) - Using 'latest' where install method supports it
    HCLOUD_VERSION=latest \
    # Add paths for tools installed in user's home (will be /root during build)
    # Ensure standard paths are also included
    PATH="/root/.cargo/bin:/root/.pulumi/bin:/root/bin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Install essential packages and dependencies
# sudo is needed by some install scripts even when running as root
# lsb-release is needed by gcloud and 1password repo setup
# ca-certificates is crucial for HTTPS downloads
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    gnupg \
    apt-transport-https \
    ca-certificates \
    lsb-release \
    unzip \
    jq \
    groff \
    less \
    bash \
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Dagger CLI
RUN cd /usr/local/bin \
    && curl -L https://dl.dagger.io/dagger/install.sh | sh \
    && dagger version

# Install uv (Python package installer/resolver)
# Installs to /root/.cargo/bin, which is added to PATH env var
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && uv --version

# Install 1Password CLI (op)
# Reference: https://developer.1password.com/docs/cli/get-started/#install
RUN curl -sS https://downloads.1password.com/linux/keys/1password.asc | \
    gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/$(dpkg --print-architecture) stable main" | \
    tee /etc/apt/sources.list.d/1password.list \
    && mkdir -p /etc/debsig/policies/AC2D62742012EA22/ \
    && curl -sS https://downloads.1password.com/linux/debian/debsig/1password.pol | \
    tee /etc/debsig/policies/AC2D62742012EA22/1password.pol \
    && mkdir -p /usr/share/debsig/keyrings/AC2D62742012EA22 \
    && curl -sS https://downloads.1password.com/linux/keys/1password.asc | \
    gpg --dearmor --output /usr/share/debsig/keyrings/AC2D62742012EA22/debsig.gpg \
    && apt-get update && apt-get install -y 1password-cli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && op --version

# Install Pulumi CLI
# Installs to /root/.pulumi/bin, which is added to PATH env var
RUN curl -fsSL https://get.pulumi.com | sh \
    # Add pulumi to path for immediate use in subsequent layers if needed
    && export PATH=$PATH:/root/.pulumi/bin \
    && pulumi version

# Install Google Cloud SDK (gcloud)
# Reference: https://cloud.google.com/sdk/docs/install#deb
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
    && apt-get update && apt-get install -y google-cloud-cli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && gcloud --version

# Install AWS CLI v2
# Reference: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws \
    && aws --version

# Install Azure CLI (az)
# Reference: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash \
    && az --version

# Install Hetzner Cloud CLI (hcloud)
# Fetches the latest release from GitHub (or specific if HCLOUD_VERSION is set)
# Installs to /usr/local/bin
RUN HCLOUD_INSTALL_DIR=/usr/local/bin \
    && if [ "$HCLOUD_VERSION" = "latest" ]; then \
       HCLOUD_DOWNLOAD_URL=$(curl -s https://api.github.com/repos/hetznercloud/cli/releases/latest | jq -r '.assets[] | select(.name | test("hcloud-linux-amd64.tar.gz$")) | .browser_download_url'); \
    else \
       HCLOUD_DOWNLOAD_URL="https://github.com/hetznercloud/cli/releases/download/v${HCLOUD_VERSION}/hcloud-linux-amd64.tar.gz"; \
    fi \
    && echo "Downloading Hetzner CLI from $HCLOUD_DOWNLOAD_URL" \
    && curl -L $HCLOUD_DOWNLOAD_URL | tar -xz -C $HCLOUD_INSTALL_DIR hcloud \
    && hcloud version

# Install Oracle Cloud Infrastructure CLI (oci)
# Reference: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm#InstallingtheCLIQuickstart
# Installs to /root/bin, which is added to PATH env var
RUN curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh | bash -s -- --accept-all-defaults \
    && oci --version