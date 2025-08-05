#!/bin/bash

# Edge Front Door Latency Testing Script
# 
# This script runs latency tests to measure the additional latency introduced
# by migrating venture-profile-api behind Edge Front Door.

set -e

# Default values
ENVIRONMENT="dev"
REQUESTS=30
OUTPUT_FILE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -e|--environment)
      ENVIRONMENT="$2"
      shift 2
      ;;
    -r|--requests)
      REQUESTS="$2"
      shift 2
      ;;
    -o|--output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Test Edge Front Door latency impact on venture-profile-api"
      echo ""
      echo "Options:"
      echo "  -e, --environment ENV    Environment to test (dev, test, prod) [default: dev]"
      echo "  -r, --requests NUM       Number of requests per endpoint [default: 30]"
      echo "  -o, --output FILE        Save detailed results to JSON file"
      echo "  -h, --help              Show this help message"
      echo ""
      echo "Examples:"
      echo "  $0 --environment dev --requests 50"
      echo "  $0 --environment prod --requests 100 --output results.json"
      exit 0
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "test" && "$ENVIRONMENT" != "prod" ]]; then
    echo "Error: Environment must be dev, test, or prod"
    exit 1
fi

# Check if Python script exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/comprehensive-tests/test_gateway_latency.py"

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Error: Cannot find $PYTHON_SCRIPT"
    exit 1
fi

echo "🚀 Starting Edge Front Door Latency Analysis"
echo "Environment: $ENVIRONMENT"
echo "Requests per endpoint: $REQUESTS"
if [[ -n "$OUTPUT_FILE" ]]; then
    echo "Output file: $OUTPUT_FILE"
fi
echo ""

# Change to the venture-profile-api directory
cd "$SCRIPT_DIR"

# Build the command
CMD="python comprehensive-tests/test_gateway_latency.py --environment $ENVIRONMENT --requests $REQUESTS"
if [[ -n "$OUTPUT_FILE" ]]; then
    CMD="$CMD --output $OUTPUT_FILE"
fi

# Run the latency test
eval $CMD

echo ""
echo "✅ Latency analysis completed!"

if [[ -n "$OUTPUT_FILE" ]]; then
    echo "📄 Detailed results saved to: $OUTPUT_FILE"
fi
