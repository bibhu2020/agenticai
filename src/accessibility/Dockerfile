# Dockerfile
FROM python:3.11-slim

apt-get update
apt-get install -y \
    libnss3 \
    libnspr4 \
    libasound2 \
    libatk1.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcups2 \
    libxss1 \
    libxshmfence1


WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# copy server and axe
COPY server.py /app/
COPY axe.min.js /app/

# install playwright browsers
RUN playwright install --with-deps

EXPOSE 8000
CMD ["python", "server.py"]
