"""Minimal OpenAI-SDK client pointed at a local Ollama server running in Kubernetes.

This script uses the modern OpenAI Python SDK (v1.x) to connect to
the Ollama-compatible endpoint (OLLAMA_URL + /v1).

Usage:
    pip install openai
    python app.py "your prompt"
"""

import os
import argparse
import sys

# Default to the NodePort 30081 defined in deploy.yml
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://172.19.202.201:30081")
MODEL = os.getenv("OLLAMA_MODEL", "ministral-3:3b")


def generate_with_openai(prompt: str, model: str = MODEL):
    try:
        from openai import OpenAI, OpenAIError
    except ImportError:
        return False, "OpenAI SDK not installed. Please run: pip install openai"

    # Configure OpenAI SDK to use local Ollama's OpenAI-compatible path
    # The client expects `base_url` to be the full path to /v1
    base_url = f"{OLLAMA_URL.rstrip('/')}/v1"
    
    try:
        # Initialize the client
        # API key is required by the SDK but ignored by Ollama
        client = OpenAI(
            base_url=base_url,
            api_key="ollama" 
        )

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        content = response.choices[0].message.content
        return True, content

    except OpenAIError as e:
        return False, f"OpenAI SDK call failed: {e}"
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"


def main():
    parser = argparse.ArgumentParser(description="Test local Ollama model via OpenAI SDK")
    parser.add_argument("prompt", nargs="+", help="Prompt text to send to the model")
    parser.add_argument("--model", default=MODEL, help="Model name to request")
    args = parser.parse_args()
    
    prompt = " ".join(args.prompt)
    print(f"Connecting to {OLLAMA_URL} using model {args.model}...")

    ok, result = generate_with_openai(prompt, model=args.model)
    if not ok:
        print(f"Error: {result}")
        sys.exit(1)
        
    print("-" * 40)
    print(result)
    print("-" * 40)


if __name__ == "__main__":
    main()
