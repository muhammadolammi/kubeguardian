FROM kubeguardian/base:latest

WORKDIR /app
ENV PYTHONPATH=/app 
USER dev 
EXPOSE 8083


CMD ["uvicorn", "orchestrator_sub.api:app", "--log-level", "info", "--host", "0.0.0.0" , "--port", "8083"]