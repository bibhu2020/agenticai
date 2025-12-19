# Ollama on Local Kubernetes

This project sets up a local Ollama instance running in a Kubernetes cluster (like Minikube or Kind), serving the `ministral-3:3b` model. It also provides a Python client (`app.py`) to interact with the model using the OpenAI SDK.

## Prerequisites

- **Docker**: For building the image.
- **Kubernetes Cluster**: A local cluster like Minikube, Kind, or MicroK8s.
- **kubectl**: Configured to talk to your cluster.
- **Python 3.x**: To run the test client.

## Setup & Deployment

1.  **Build and Deploy**:
    The included `build.sh` script handles building the Docker image, creating the `ollama` namespace, and deploying the resources.

    ```bash
    ./build.sh
    ```

    **Note for Minikube/Kind users**:
    If you are using Minikube or Kind, you might need to load the image into the cluster before deploying if the build happens on your host machine.
    - **Minikube**: `minikube image load ollama-ministral-3b:local`
    - **Kind**: `kind load docker-image ollama-ministral-3b:local`

2.  **Verify Deployment**:
    Check if the pod is running:

    ```bash
    kubectl get pods -n ollama
    ```

3.  **Port Forwarding (if needed)**:
    The deployment uses a NodePort (30080).
    - If using **Minikube**: You might need `minikube tunnel` running in a separate terminal to access NodePorts, or use `kubectl port-forward`:
      ```bash
      kubectl port-forward svc/ollama-ministral-3b-svc -n ollama 30080:8080
      ```
    - If using **WSL/Localhost**: The service should be accessible at `http://172.19.202.201:30080`.

## Testing the Model

We use the standard OpenAI Python SDK to talk to Ollama, as Ollama provides an OpenAI-compatible API.

1.  **Install Dependencies**:

    ```bash
    pip install openai
    ```

2.  **Run the Client**:
    The `app.py` script sends a prompt to your local model.

    ```bash
    # Default prompt
    python app.py "Why is the sky blue?"

    # Custom model (if you deployed a different one)
    python app.py "Tell me a joke" --model ministral-3:3b
    ```

## Project Structure

- **`Dockerfile`**: Builds an image based on `ollama/ollama` and pulls the `ministral-3:3b` model baked in.
- **`deploy.yml`**: Kubernetes Deployment and Service (NodePort 30080).
- **`build.sh`**: Helper script to build the image and apply k8s manifests.
- **`app.py`**: Python client demonstrating how to use the `openai` library with the local Ollama endpoint.
