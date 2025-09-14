FROM kubeguardian/base:latest

RUN apt-get update && apt-get install -y curl tar unzip bash \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV PYTHONPATH=/app 
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8084

CMD ["uvicorn", "chat.api:app", "--log-level", "info", "--host", "0.0.0.0" , "--port", "8084"]