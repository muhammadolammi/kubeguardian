FROM debian:bookworm-slim AS runtime
ENV DEBIAN_FRONTEND=noninteractive

# Install minimal deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -sSL "https://dl.k8s.io/release/v1.33.0/bin/linux/amd64/kubectl" -o /usr/local/bin/kubectl && \
    chmod +x /usr/local/bin/kubectl

# Install kubectl-ai from GitHub release
RUN curl -sSL "https://github.com/GoogleCloudPlatform/kubectl-ai/releases/download/v0.0.25/kubectl-ai_v0.0.25_linux_amd64.tar.gz" \
    | tar -xz -C /usr/local/bin && \
    chmod +x /usr/local/bin/kubectl-ai


ENTRYPOINT ["/usr/local/bin/kubectl-ai"]
