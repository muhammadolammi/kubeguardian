FROM kubeguardian/base:latest

WORKDIR /app
ENV PYTHONPATH=/app 
USER dev 

EXPOSE 8081


CMD ["uvicorn", "guardian.api:app", "--log-level", "info", "--host", "0.0.0.0" , "--port", "8081"]