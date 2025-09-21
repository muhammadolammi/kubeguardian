## ------------------------------- Builder Stage ------------------------------ ## 
## ------------------------------- Builder Stage ------------------------------ ## 
FROM python:3.13-bookworm AS builder

WORKDIR /app

# Install deps first (cached if unchanged)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

## ------------------------------- Production Stage ------------------------------ ##
FROM python:3.13-slim-bookworm AS production

WORKDIR /app

# Copy installed deps
COPY --from=builder /install /usr/local

# Copy app source
COPY . .
ENV PYTHONPATH=/APP 

CMD [ "python" ,"-m" ,  "main"]
 