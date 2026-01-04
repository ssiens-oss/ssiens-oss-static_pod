#!/bin/bash
# Printify Push - Standalone script that can be run from anywhere

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the project directory
cd "$SCRIPT_DIR"

# Run the TypeScript script
npm run printify:push
