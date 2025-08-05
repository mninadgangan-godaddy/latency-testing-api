# Simple Health Check Latency Testing

Simple tool for comparing latency between old direct endpoints and new Edge Front Door endpoints for health check endpoints only.

## Usage

**Run from project root using `uv run`:**

```bash
# Basic health check test
uv run simple-health-check/test_health_check.py --environment dev

# Test with more requests
uv run simple-health-check/test_health_check.py --environment dev --requests 50

# Test production environment
uv run simple-health-check/test_health_check.py --environment prod --requests 100
```

**Alternative - if dependencies are installed:**
```bash
cd simple-health-check
python test_health_check.py --environment dev
```

## Arguments

- `--environment, -e`: Environment to test (`dev`, `test`, `prod`) - default: `dev`
- `--requests, -r`: Number of requests per endpoint - default: `30`

## Example Output

```
Testing dev environment health check latency...
Old endpoint: https://venture.mvciapi.dev.aws.gdcld.net/health-check
New endpoint: https://venture-profile-api.frontdoor.dev-godaddy.com/health-check
Running 30 requests to each endpoint...

======================================================================
HEALTH CHECK LATENCY COMPARISON
======================================================================
Environment: dev
Successful requests: 30 old, 30 new

Metric     Old (ms)     New (ms)     Difference (ms) % Change  
----------------------------------------------------------------------
MEAN       211.08       209.58       -1.50           -0.7      %
MEDIAN     209.29       208.84       -0.45           -0.2      %
P95        216.33       210.11       -6.22           -2.9      %
P99        234.88       225.58       -9.31           -4.0      %

📊 Summary: Gateway is 1.50ms faster on average
```

## Authentication

For environments requiring authentication, set the `AUTH_TOKEN` environment variable:

```bash
export AUTH_TOKEN="your-sso-jwt-token"
uv run simple-health-check/test_health_check.py --environment test
```

The tool will automatically add the token as `Authorization: sso-jwt {token}` header.
