FROM kubeguardian/base:latest

WORKDIR /app
ENV PYTHONPATH=/app 
USER dev 


CMD ["uvicorn", "orchestrator_pub.api:app", "--log-level", "info", "--host", "0.0.0.0" , "--port", "8082"]