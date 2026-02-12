# 1. Base Image: Use a lightweight, official Python version
FROM python:3.13.9-slim

# 2. Prevent Python from writing .pyc files (useless in containers)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set work directory
WORKDIR /app

# 4. Install SYSTEM dependencies (Critical for PDF/Image work)
# We add 'build-essential' and 'libgl1' because many Python PDF libs need them.
# Removed 'libgl1-mesa-glx' as it's not necessary for most cases.
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Install NPM package for the Signature Pad
# We copy ONLY the package files first to help with Docker caching
COPY apps/z83_form/static/package*.json ./apps/z83_form/static/
RUN cd apps/z83_form/static && npm install

# 7. Copy the rest of your code (app.py, apps/, common/, etc.)
COPY . .

# 8. Expose the port Gunicorn will use
EXPOSE 3000

# 9. The Start Command
# This runs your 'app' object inside 'app.py'
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:3000", "app:app"]