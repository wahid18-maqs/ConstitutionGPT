# Use a lightweight Python base image
FROM python:3.9-slim

# Set a working directory inside the container
WORKDIR /app

# Install system dependencies (useful for certain Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory to the container
COPY . /app/

# Expose the port FastAPI will run on
EXPOSE 8000

# Install Python-dotenv for environment variable loading
RUN pip install python-dotenv

# Start FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
