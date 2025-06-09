FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY examples/ ./examples/
COPY README.md LICENSE ./

# Create directories for data processing
RUN mkdir -p /app/data /app/output /app/reports

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN useradd -m -u 1000 twitter-parser && \
    chown -R twitter-parser:twitter-parser /app
USER twitter-parser

# Default command
CMD ["python", "-m", "scripts.extract_tweets", "--help"]