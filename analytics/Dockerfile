FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y gcc postgresql-client

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5153

# Run the application
CMD ["python", "app.py"] 