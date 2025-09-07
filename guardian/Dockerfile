FROM kubeguardian/base:latest

WORKDIR /app
ENV PYTHONPATH=/app 
USER dev 


CMD ["uvicorn", "chat.api:app", "--log-level", "info", "--host", "0.0.0.0" , "--port", "8081"]