FROM kubeguardian/base:latest
RUN apt-get update && apt-get install -y curl tar unzip bash \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV PYTHONPATH=/app 
EXPOSE 8083


CMD ["python", "-m", "orchestrator.sub.sub"]