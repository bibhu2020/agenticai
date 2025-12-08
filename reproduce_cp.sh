#!/bin/bash
# Reproduction script for cp inconsistency

mkdir -p test_cp_issue
cd test_cp_issue

# Setup source
mkdir -p src/healthcare-assistant
touch src/healthcare-assistant/file1.txt

mkdir -p data/healthcare
touch data/healthcare/file2.txt

# Setup target
mkdir -p deploy_temp

# Run commands as per workflow
# Note: In the workflow, 'cp' is used.
echo "Running: cp -r src/healthcare-assistant deploy_temp/src/"
cp -r src/healthcare-assistant deploy_temp/src/

echo "Running: cp -r data/healthcare deploy_temp/data/"
cp -r data/healthcare deploy_temp/data/

# Check results
echo "Structure of deploy_temp:"
find deploy_temp -maxdepth 3
