# Health Check vs Real Endpoints: Latency Analysis

## The Problem with Health-Check-Only Testing

Testing only `/health-check` provides **misleading results** that don't represent real-world performance impact of Edge Front Door.

## Comparison of Endpoint Characteristics

| Aspect | Health Check | Real API Endpoints |
|--------|-------------|-------------------|
| **Authentication** | ❌ None | ✅ SSO JWT validation |
| **Processing** | ❌ `return {"status": "ok"}` | ✅ Business logic + external calls |
| **Response Size** | ❌ ~20 bytes | ✅ 100B - 5KB+ |
| **Dependencies** | ❌ None | ✅ External HTTP services |
| **Headers** | ❌ Minimal | ✅ Auth, content-type, etc. |
| **Caching** | ❌ Not representative | ✅ Real caching behavior |
| **Error Handling** | ❌ Always 200 OK | ✅ 4xx/5xx possible |

## Real Performance Factors Missing from Health Check

### 1. **Authentication Overhead**
```python
# Health check - no auth
GET /health-check
→ {"status": "ok"}

# Real endpoint - full auth pipeline  
GET /v1/customer/.../venture/.../inferred/brands
Authorization: Bearer <JWT_TOKEN>
→ JWT validation + external service calls + business logic
```

### 2. **Payload Size Impact**
- **Health check**: 20 bytes `{"status":"ok"}`
- **Brands status**: ~200 bytes (JSON with multiple fields)
- **Brands data**: 2KB+ (complex JSON with arrays)
- **Edge Front Door may handle larger payloads differently**

### 3. **Network Characteristics**
- **Request headers**: Auth tokens, content negotiation
- **Response headers**: CORS, content-type, custom headers
- **Connection patterns**: Keep-alive behavior differs

## Recommended Testing Strategy

### ✅ **Multi-Tier Approach**

#### **Tier 1: Baseline (Health Check)**
- Purpose: Basic connectivity test
- Endpoint: `/health-check`
- Characteristics: No auth, minimal processing, tiny response

#### **Tier 2: Moderate Load (Status Endpoints)**
- Purpose: Typical API usage patterns
- Endpoints: `/.../brands/status`, `/.../logo-url`
- Characteristics: Auth required, moderate processing, small responses

#### **Tier 3: Heavy Load (Data Endpoints)**
- Purpose: Worst-case scenarios
- Endpoints: `/.../brands`, `/.../compliance/...`
- Characteristics: Auth + heavy processing + large responses

### **Usage Examples**

```bash
# Quick health check only (limited value)
uv run quick_latency_test.py

# Comprehensive multi-endpoint test (recommended)
uv run enhanced_latency_test.py --environment dev --requests 15

# Full authenticated test suite
./run_latency_test.sh --environment prod --requests 30
```

## Expected Results Differences

### **Health Check Results (Misleading)**
```
Health Check: Old 45ms → New 47ms (+2ms, +4%)
```
**❌ Conclusion**: "Edge Front Door adds minimal latency"

### **Real Endpoint Results (Accurate)**
```
Health Check:   Old  45ms → New  47ms (+2ms,  +4%)
Brands Status:  Old  89ms → New 103ms (+14ms, +16%)  
Brands Data:    Old 156ms → New 187ms (+31ms, +20%)
Logo URL:       Old  67ms → New  78ms (+11ms, +16%)
```
**✅ Conclusion**: "Edge Front Door adds 10-30ms depending on endpoint complexity"

## Key Insights

### **Why Health Check Underestimates Impact**

1. **No authentication overhead**: Real auth adds 5-15ms
2. **Minimal processing**: No external service calls to amplify latency
3. **Tiny responses**: Network serialization differences not apparent
4. **No error scenarios**: 4xx/5xx responses may have different characteristics

### **What Real Testing Reveals**

1. **Authentication latency**: JWT validation through Edge Front Door
2. **Payload impact**: Larger responses show more significant overhead  
3. **Processing amplification**: External service latency gets amplified
4. **Realistic percentiles**: P95/P99 latencies more representative

## Recommendations

### **For Development Testing**
```bash
# Quick assessment (health check acceptable for speed)
uv run quick_latency_test.py
```

### **For Production Validation**
```bash
# Comprehensive test with real endpoints
uv run enhanced_latency_test.py --environment prod --requests 25
```

### **For Ongoing Monitoring**
```bash
# Regular monitoring with representative endpoints
./run_latency_test.sh --environment prod --requests 50
```

## Bottom Line

**Health check testing alone is insufficient** for production migration decisions. It's like testing a race car by only checking if the engine starts - you need to test actual driving performance under realistic conditions.

Use health check for quick connectivity verification, but always validate with real authenticated endpoints that represent your actual traffic patterns.
