FROM python:3.12-slim
WORKDIR /app

# Install system dependencies including MySQL client libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    pkg-config \
    default-libmysqlclient-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for mysqlclient compilation
ENV MYSQLCLIENT_CFLAGS="-I/usr/include/mariadb"
ENV MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmariadb"

COPY requirements.txt .

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copies the application code to .
COPY . .
EXPOSE 8000

# Run the app with uvicorn using centralized logging
CMD [ "python", "common_logging_startup.py" ]
