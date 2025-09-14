FROM kubeguardian/base:latest


# Install kubectl-ai
# Install OS packages (can be cached)
RUN apt-get update && apt-get install -y curl tar unzip bash \
    && rm -rf /var/lib/apt/lists/*

# Download kubectl-ai tarball and copy it into the image
ADD https://github.com/GoogleCloudPlatform/kubectl-ai/releases/download/v0.0.25/kubectl-ai_Linux_x86_64.tar.gz /tmp/kubectl-ai.tar.gz

# Extract and move binary (can be cached if ADD file didn't change)
RUN tar -xzf /tmp/kubectl-ai.tar.gz -C /tmp \
    && mv /tmp/kubectl-ai /usr/local/bin/kubectl-ai \
    && chmod +x /usr/local/bin/kubectl-ai \
    && rm /tmp/kubectl-ai.tar.gz
WORKDIR /app
ENV PYTHONPATH=/app 

EXPOSE 8081
 

CMD ["uvicorn", "guardian.api:app", "--log-level", "info", "--host", "0.0.0.0" , "--port", "8081"]