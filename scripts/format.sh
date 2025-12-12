#!/bin/bash
# Ruff linting and formatting script
# Run this before committing code

set -e

echo "Running Ruff linter and formatter..."

# Check for lint issues
echo "Checking for lint issues..."
ruff check --fix app tests

# Format code
echo "Formatting code..."
ruff format app tests

echo "✓ Code formatting complete!"
