#!/bin/bash
# Test the FIX for cp inconsistency

rm -rf deployed_temp_fixed

# Setup source
mkdir -p src/healthcare-assistant
touch src/healthcare-assistant/file1.txt

mkdir -p data/healthcare
touch data/healthcare/file2.txt

# Setup target
mkdir -p deploy_temp_fixed

# FIX: Explicitely create parent directories
mkdir -p deploy_temp_fixed/src
mkdir -p deploy_temp_fixed/data

# Run commands
echo "Running: cp -r src/healthcare-assistant deploy_temp_fixed/src/"
cp -r src/healthcare-assistant deploy_temp_fixed/src/

echo "Running: cp -r data/healthcare deploy_temp_fixed/data/"
cp -r data/healthcare deploy_temp_fixed/data/

# Check results
echo "Structure of deploy_temp_fixed:"
find deploy_temp_fixed -maxdepth 3
