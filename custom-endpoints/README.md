# Custom Endpoint Latency Testing

Advanced tool for testing custom business endpoints with configurable customer and venture IDs.

## Usage

```bash
# Basic test with customer and venture IDs
python test_custom_endpoints.py --customer-id 12345 --venture-id abcdef --environment dev

# Test with authentication
AUTH_TOKEN="your-token-here" python test_custom_endpoints.py --customer-id 12345 --venture-id abcdef --environment prod

# Test with more requests
python test_custom_endpoints.py --customer-id 12345 --venture-id abcdef --environment dev --requests 50

# Test custom endpoints
python test_custom_endpoints.py --customer-id 12345 --venture-id abcdef --environment dev --endpoints "/v1/customer/{customer_id}/venture/{venture_id}/custom-endpoint"
```

## Arguments

- `--customer-id, -c`: Customer ID for API endpoints (required)
- `--venture-id, -v`: Venture ID for API endpoints (required)  
- `--environment, -e`: Environment to test (`dev`, `test`, `prod`) - default: `dev`
- `--requests, -r`: Number of requests per endpoint - default: `30`
- `--endpoints`: Custom endpoints to test (optional, uses defaults if not provided)

## Authentication

Set the `AUTH_TOKEN` environment variable to test authenticated endpoints:

```bash
export AUTH_TOKEN="your-bearer-token"
python test_custom_endpoints.py --customer-id 12345 --venture-id abcdef
```

## Default Endpoints Tested

- `/v1/customer/{customer_id}/venture/{venture_id}/inferred/brands/status`
- `/v1/customer/{customer_id}/venture/{venture_id}/inferred/logo-url`
- `/v1/customer/{customer_id}/venture/{venture_id}/profile`

## Example Output

```
Starting latency analysis for dev environment...
Customer ID: 12345
Venture ID: abcdef
Testing 30 requests per endpoint
Using AUTH_TOKEN for authentication

================================================================================
CUSTOM ENDPOINT LATENCY ANALYSIS
================================================================================

Endpoint: /v1/customer/12345/venture/abcdef/inferred/brands/status
------------------------------------------------------------
Old URL: https://venture.mvciapi.dev.aws.gdcld.net
New URL: https://venture-profile-api.frontdoor.dev-godaddy.com

Metric     Old (ms)     New (ms)     Additional (ms) % Increase  
----------------------------------------------------------------------
MEAN       207.70       206.02       -1.67           -0.8        %
MEDIAN     207.57       206.00       -1.58           -0.8        %
P95        208.94       207.66       -1.28           -0.6        %
P99        211.23       207.97       -3.26           -1.5        %

Successful requests: 30 old, 30 new
📊 Average latency difference: -1.67ms (gateway is faster)
```
