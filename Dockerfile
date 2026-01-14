FROM python:3.10

# Prevent Python from writing .pyc files and ensure output is unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy application code and set working directory
COPY . /app/
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root user and required directories
RUN useradd --no-create-home admin && \
    mkdir -p staticfiles && \
    chown -R admin:admin .

# Switch to non-root user for security
USER admin:admin