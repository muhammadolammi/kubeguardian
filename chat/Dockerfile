FROM kubeguardian/base:latest

WORKDIR /app

#Already coppied in base
# COPY ./api.py /app/
EXPOSE  8080
CMD ["uvicorn", "chat.api:app", "--host", "0.0.0.0", "--port", "8080"]

