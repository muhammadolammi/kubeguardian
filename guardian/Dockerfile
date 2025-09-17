FROM kubeguardian/base
WORKDIR /app

# Install kubectl-ai
# Install OS packages (can be cached)
RUN apt-get update && apt-get install -y curl  \
    && rm -rf /var/lib/apt/lists/*

CMD ["sh", "-c", "uvicorn guardian.main:app --host 0.0.0.0 --port 8081"]
 