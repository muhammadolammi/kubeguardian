# base/Dockerfile
FROM python:3.12-slim

WORKDIR /app
# Copy only requirements first
COPY requirements.txt ./requirements.txt

# Install dependencies (cached if requirements.txt doesn't change)
RUN pip install --no-cache-dir -r requirements.txt
#COPY everything so all sub-images can use the files and package
COPY . /app/
