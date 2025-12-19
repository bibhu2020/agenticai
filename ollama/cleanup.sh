#!/usr/bin/env bash
set -e

NAMESPACE="ollama"
IMAGE_NAME="ollama-ministral-3b:local"

echo "Undeploying resources..."
echo "Deleting namespace '${NAMESPACE}' (this may take a few seconds)..."
if kubectl get namespace "${NAMESPACE}" >/dev/null 2>&1; then
    kubectl delete namespace "${NAMESPACE}"
    echo "Namespace '${NAMESPACE}' deleted."
else
    echo "Namespace '${NAMESPACE}' not found, skipping."
fi

echo "Removing Docker image '${IMAGE_NAME}'..."
if docker image inspect "${IMAGE_NAME}" >/dev/null 2>&1; then
    docker rmi "${IMAGE_NAME}"
    echo "Image '${IMAGE_NAME}' removed."
else
    echo "Image '${IMAGE_NAME}' not found, skipping."
fi

echo "Cleanup complete."
