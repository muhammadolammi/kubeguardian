FROM kubeguardian/base:latest

WORKDIR /app
ENV PYTHONPATH=/app 
USER dev 
EXPOSE 8082

CMD ["python", "-m", "orchestrator_pub.pub"]