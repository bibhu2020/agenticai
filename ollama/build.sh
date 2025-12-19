#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="ollama-ministral-3b:local"
NAMESPACE="ollama"
# Handle the case where BASH_SOURCE is empty (e.g. zsh or sourced differently)
SCRIPT_PATH="${BASH_SOURCE[0]:-$0}"
BUILD_DIR="$(cd "$(dirname "${SCRIPT_PATH}")" && pwd)"
DEPLOY_FILE="${BUILD_DIR}/deploy.yml"

echo "Building Docker image: ${IMAGE_NAME} from ${BUILD_DIR}"
docker build -t "${IMAGE_NAME}" "${BUILD_DIR}"
echo "Built ${IMAGE_NAME}"

echo "Transferring image to MicroK8s..."
# MicroK8s needs the image imported manually if using the local docker daemon
docker save "${IMAGE_NAME}" > "${IMAGE_NAME}.tar"
microk8s ctr image import "${IMAGE_NAME}.tar"
rm "${IMAGE_NAME}.tar"
echo "Image imported to MicroK8s."

echo "Ensuring namespace '${NAMESPACE}' exists..."
microk8s kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | microk8s kubectl apply -f -

echo "Deploying to namespace '${NAMESPACE}'..."
if [ -f "${DEPLOY_FILE}" ]; then
    microk8s kubectl apply -f "${DEPLOY_FILE}" -n "${NAMESPACE}"
    echo "Deployment applied."
    echo "Check status with: kubectl get pods -n ${NAMESPACE}"
else
    echo "Error: ${DEPLOY_FILE} not found!"
    exit 1
fi

echo "To access the service, see the NodePort in the deploy.yml or run:"
echo "microk8s kubectl get svc -n ${NAMESPACE}"
