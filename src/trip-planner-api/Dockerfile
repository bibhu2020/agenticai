# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the HF Spaces default port
EXPOSE 7860

# Run Uvicorn on port 7860 (HF Spaces only exposes 7860)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
