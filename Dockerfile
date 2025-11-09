FROM python:3.13-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bot/ ./bot/

# Use virtual environment's Python
ENV PATH="/app/venv/bin:$PATH"

# Run the bot
CMD ["python", "-m", "bot"]
