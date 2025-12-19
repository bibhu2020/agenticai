# Use the official Ollama image as a base (includes Ollama runtime)
# This will pull the model at build time so the image contains the model.
FROM ollama/ollama:latest

# We need to start the Ollama server in the background to allow 'ollama pull' to run.
# The server is only running temporarily for this build step.
RUN ollama serve & sleep 5 && ollama pull ministral-3:3b

# Expose the default serve port
EXPOSE 8080

# Run the Ollama server to serve models over HTTP
# Adjust flags as needed for your Ollama version
CMD ["ollama", "serve", "--host", "0.0.0.0", "--port", "8080"]
