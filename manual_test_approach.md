# Manual Testing Approach - All Environments & Endpoints

Based on the authentication issues, here's how to manually test all environments comprehensively:

## 🎯 What We Discovered So Far

### Partial Results from Quick Test:
```
Environment | Old URL (ms) | New URL (ms) | Additional | Status
-----------|-------------|-------------|-----------|--------
dev        | 206         | N/A         | N/A       | ❌ Auth required
test       | 211         | N/A         | N/A       | ❌ Auth required  
prod       | 211         | 271         | +60ms     | ⚠️ 28% increase!
```

**Key Finding**: Production shows **60ms additional latency (28% increase)** - much higher than the original 13.8ms estimate!

## 🔧 Manual Testing Options

### Option 1: Test Production Only (Working)
Since prod is responding, focus comprehensive testing there:

```bash
# Test prod with different request counts
uv run quick_latency_test.py  # Focus on prod results

# Or run specific prod test
echo "Testing prod extensively..."
```

### Option 2: Fix Authentication for All Environments

#### Step 1: Check SSO Status
```bash
# Check if you're logged in
aws sts get-caller-identity

# If not logged in, authenticate
aws sso login --profile godaddy-dev  # or appropriate profile
```

#### Step 2: Set Environment Variables
```bash
# Set the correct SSO domain
export SSO_GODADDY_DOMAIN="sso.dev-godaddy.com"  # or correct domain

# Test auth
echo $SSO_GODADDY_DOMAIN
```

#### Step 3: Re-run Enhanced Test
```bash
uv run enhanced_latency_test.py --environment dev --requests 10
```

### Option 3: Use Direct URLs for Manual Testing

Test each environment manually with curl:

```bash
# Test old URLs (should work)
curl -w "@curl-format.txt" https://venture.mvciapi.dev.aws.gdcld.net/health-check
curl -w "@curl-format.txt" https://venture.mvciapi.stage.aws.gdcld.net/health-check  
curl -w "@curl-format.txt" https://venture.mvciapi.prod.aws.gdcld.net/health-check

# Test new URLs (may need auth)
curl -w "@curl-format.txt" https://venture-profile-api.frontdoor.dev-godaddy.com/health-check
curl -w "@curl-format.txt" https://venture-profile-api.frontdoor.test-godaddy.com/health-check
curl -w "@curl-format.txt" https://venture-profile-api.frontdoor.godaddy.com/health-check
```

### Option 4: Environment-Specific Testing

#### Test Each Environment Separately:
```bash
# DEV
./run_latency_test.sh --environment dev --requests 20

# TEST  
./run_latency_test.sh --environment test --requests 20

# PROD
./run_latency_test.sh --environment prod --requests 20
```

## 📋 Curl Format File for Manual Testing

Create `curl-format.txt`:
```
     time_namelookup:  %{time_namelookup}s\n
        time_connect:  %{time_connect}s\n
     time_appconnect:  %{time_appconnect}s\n
    time_pretransfer:  %{time_pretransfer}s\n
       time_redirect:  %{time_redirect}s\n
  time_starttransfer:  %{time_starttransfer}s\n
                     ----------\n
          time_total:  %{time_total}s\n
           http_code:  %{http_code}\n
```

## 🎯 Recommended Immediate Actions

### 1. **Validate Production Results**
The 60ms additional latency in prod is concerning. Run more comprehensive prod tests:

```bash
# Extended prod testing
time for i in {1..50}; do 
  curl -s -w "%{time_total}\n" -o /dev/null https://venture.mvciapi.prod.aws.gdcld.net/health-check
done > old_prod_times.txt

time for i in {1..50}; do 
  curl -s -w "%{time_total}\n" -o /dev/null https://venture-profile-api.frontdoor.godaddy.com/health-check
done > new_prod_times.txt
```

### 2. **Investigate Authentication Requirements**
Check if Edge Front Door requires auth even for health-check:

```bash
# Test with different endpoints
curl -I https://venture-profile-api.frontdoor.dev-godaddy.com/health-check
curl -I https://venture-profile-api.frontdoor.dev-godaddy.com/docs
```

### 3. **Get Proper SSO Configuration**
Contact your DevOps team for:
- Correct SSO domain configuration
- Proper authentication setup for testing
- Service account credentials if needed

## 📊 Expected Next Steps

1. **Immediate**: Focus on prod testing since it's working
2. **Short-term**: Fix authentication for dev/test
3. **Complete**: Run full multi-endpoint, multi-environment tests
4. **Analysis**: Generate comprehensive reports

## 🚨 Current Status Summary

- ✅ **Found significant latency impact**: 60ms in prod (not 13.8ms!)
- ⚠️ **Authentication blocking dev/test**: Need SSO setup
- ✅ **Proof of concept working**: Can measure real gateway impact
- 🎯 **Next priority**: Fix auth and run complete tests
