#!/usr/bin/env bash
set -e

echo "Attempting to fix MicroK8s CNI 'Unauthorized' error..."

echo "1. Restarting MicroK8s..."
sudo microk8s stop
sudo microk8s start

echo "2. Waiting for MicroK8s to be ready..."
sudo microk8s status --wait-ready

echo "3. Restarting Calico pods..."
# Sometimes restarting the calico-node pods forces them to refresh tokens
sudo microk8s kubectl -n kube-system rollout restart daemonset/calico-node

echo "4. Deleting the stuck ollama pod to force recreation..."
sudo microk8s kubectl -n ollama delete pod -l app=ollama-ministral-3b --force --grace-period=0

echo "Done. Please check pod status with: microk8s kubectl get pods -n ollama"
