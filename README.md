# Edge Front Door Latency Testing

Simple and focused latency testing tools for measuring Edge Front Door performance impact.

## Project Structure

This project is organized into 2 main directories:

### 📊 `simple-health-check/`
**Simple health check latency comparison**
- Tests only `/health-check` endpoints
- No authentication required
- Perfect for quick performance checks
- [Documentation](simple-health-check/README.md)

```bash
uv run simple-health-check/test_health_check.py --environment dev --requests 50
```

### 🔧 `custom-endpoints/`
**Customizable endpoint testing with customer/venture IDs**
- Test business endpoints with real customer data
- Configurable customer ID and venture ID parameters
- Supports authentication via `AUTH_TOKEN`
- [Documentation](custom-endpoints/README.md)

```bash
uv run custom-endpoints/test_custom_endpoints.py --customer-id 12345 --venture-id abcdef --environment dev
```

## Quick Start

### Option 1: Simple Health Check
```bash
# Run from project root
uv run simple-health-check/test_health_check.py --environment dev
```

### Option 2: Custom Endpoints
```bash
# Run from project root with your customer/venture IDs
uv run custom-endpoints/test_custom_endpoints.py \
  --customer-id your-customer-id \
  --venture-id your-venture-id \
  --environment dev \
  --requests 30
```

## Installation

Install dependencies:
```bash
uv sync
# or
pip install httpx
```

## Environments

All tools support these environments:
- `dev` - Development environment (default)
- `test` - Test/staging environment  
- `prod` - Production environment

## Output

Both tools provide detailed latency analysis including:
- Mean, median, P95, P99 latency metrics
- Direct comparison between old and new endpoints
- Clear summary of performance impact

## Authentication

For endpoints requiring authentication, set the `AUTH_TOKEN` environment variable:

```bash
export AUTH_TOKEN="your-sso-jwt-token"
# Then run your tests
```

The tools will automatically add the token as `Authorization: sso-jwt {token}` header.
