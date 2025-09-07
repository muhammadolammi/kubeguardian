FROM kubeguardian/base:latest

WORKDIR /app
ENV PYTHONPATH=/app 
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8084

# Change user from root
USER dev 
CMD ["uvicorn", "chat.api:app", "--log-level", "info", "--host", "0.0.0.0" , "--port", "8084"]