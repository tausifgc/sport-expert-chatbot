#!/bin/bash

# Quick deploy script - runs the main deployment script
# This allows you to run ./deploy.sh from the root folder

set -e

# Run the deployment script from the deployment folder
./deployment/deploy-cloud-build.sh
