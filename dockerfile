FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for pyodbc and ODBC driver
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    libodbc1 \
    curl \
    gnupg2 \
    apt-transport-https \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Add Microsoft repository and install SQL Server ODBC driver
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-archive-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/debian/$(lsb_release -rs)/prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and setup the application
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]