FROM python:3.13-slim

WORKDIR /app

# Copy requirements and entrypoint (change less frequently)
COPY requirements.txt .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create virtual environment and install dependencies
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Use virtual environment's Python
ENV PATH="/app/venv/bin:$PATH"

# Copy application code (changes most frequently)
COPY bot/ ./bot/

ENTRYPOINT ["/entrypoint.sh"]
