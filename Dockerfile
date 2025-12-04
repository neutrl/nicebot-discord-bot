# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot files
COPY discord_bot.py .
COPY commands/ ./commands/

# Create directory for persistent data
RUN mkdir -p /app/data

# Run the bot
CMD ["python", "discord_bot.py"]
