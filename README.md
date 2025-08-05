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
cd simple-health-check
python test_health_check.py --environment dev --requests 50
```

### 🔧 `custom-endpoints/`
**Customizable endpoint testing with customer/venture IDs**
- Test business endpoints with real customer data
- Configurable customer ID and venture ID parameters
- Supports authentication via `AUTH_TOKEN`
- [Documentation](custom-endpoints/README.md)

```bash
cd custom-endpoints
python test_custom_endpoints.py --customer-id 12345 --venture-id abcdef --environment dev
```

## Quick Start

### Option 1: Simple Health Check
```bash
# Navigate to simple health check directory
cd simple-health-check

# Run basic health check test
python test_health_check.py --environment dev
```

### Option 2: Custom Endpoints
```bash
# Navigate to custom endpoints directory  
cd custom-endpoints

# Run test with your customer/venture IDs
python test_custom_endpoints.py \
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
export AUTH_TOKEN="your-bearer-token"
# Then run your tests
```
