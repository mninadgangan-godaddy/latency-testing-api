# Edge Front Door Latency Testing

This directory contains tools to measure the additional latency introduced by migrating the venture-profile-api behind Edge Front Door.

## Overview

The venture-profile-api has been migrated from direct endpoints to Edge Front Door:

**Old URLs (Direct):**
- dev: `https://venture.mvciapi.dev.aws.gdcld.net`
- test: `https://venture.mvciapi.stage.aws.gdcld.net`  
- prod: `https://venture.mvciapi.prod.aws.gdcld.net`

**New URLs (Edge Front Door):**
- dev: `https://venture-profile-api.frontdoor.dev-godaddy.com`
- test: `https://venture-profile-api.frontdoor.test-godaddy.com`
- prod: `https://venture-profile-api.frontdoor.godaddy.com`

## Running the Latency Test

### Basic Usage

```bash
# Test dev environment with 30 requests per endpoint
python test_gateway_latency.py --environment dev

# Test prod environment with 100 requests for more accuracy
python test_gateway_latency.py --environment prod --requests 100

# Save detailed results to a JSON file
python test_gateway_latency.py --environment test --requests 50 --output latency_results.json
```

### Prerequisites

Ensure you have the required dependencies installed (they should already be available in the venture-profile-api project):
- `httpx` - For async HTTP requests
- `gd_auth` - For authentication
- `mvci_logging` - For logging

### What the Test Measures

The script tests multiple endpoints and measures:
- **Mean latency** - Average response time
- **Median latency** - 50th percentile response time
- **P95 latency** - 95th percentile response time
- **P99 latency** - 99th percentile response time
- **Additional latency** - The difference introduced by the gateway

### Sample Output

```
================================================================================
EDGE FRONT DOOR LATENCY ANALYSIS
================================================================================

Endpoint: /health
------------------------------------------------------------
Old URL: https://venture.mvciapi.dev.aws.gdcld.net
New URL: https://venture-profile-api.frontdoor.dev-godaddy.com

Metric          Old (ms)     New (ms)     Additional (ms) % Increase  
----------------------------------------------------------------------
MEAN            45.23        52.18        6.95            15.4%
MEDIAN          42.10        49.33        7.23            17.2%
P95             67.45        78.22        10.77           16.0%
P99             89.12        102.45       13.33           14.9%

Successful requests: 30 old, 30 new
📊 Average additional latency: +6.95ms (15.4% increase)
```

## Understanding the Results

### Key Metrics to Focus On:
- **Mean additional latency**: The average overhead introduced by the gateway
- **P95 additional latency**: The overhead for the worst 5% of requests
- **Percentage increase**: How much slower the gateway makes requests

### Typical Expectations:
- **Good**: Additional latency < 10ms (< 20% increase)
- **Acceptable**: Additional latency 10-25ms (20-50% increase)
- **Concerning**: Additional latency > 25ms (> 50% increase)

### Factors Affecting Results:
- **Network location**: Results vary based on where you run the test
- **Time of day**: Different results during peak vs off-peak hours
- **Geographic distance**: Edge Front Door may route differently than direct connections
- **Caching**: The gateway may cache responses, improving performance over time

## Automated Testing

You can also run this as part of your CI/CD pipeline to monitor latency over time:

```bash
# Run and save results with timestamp
python test_gateway_latency.py \
  --environment prod \
  --requests 50 \
  --output "latency_$(date +%Y%m%d_%H%M%S).json"
```

## Troubleshooting

### Authentication Issues
If you get authentication errors, ensure:
1. You're logged into the appropriate SSO
2. Your credentials have access to the venture-profile-api
3. The `SSO_GODADDY_DOMAIN` environment variable is set

### Network Issues
- Run the test multiple times to account for network variability
- Test from different network locations if possible
- Consider testing during different times of day

### Inconsistent Results
- Increase the number of requests (`--requests 100+`) for more stable averages
- Check if either endpoint is experiencing issues
- Verify both endpoints are serving the same version of the API
