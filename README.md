# 🚀 Edge Front Door Latency Testing Suite

A comprehensive toolkit for measuring the latency impact of API gateway migrations. Originally developed to test Edge Front Door performance but adaptable for any gateway latency analysis.

## 🎯 Purpose

This toolkit helps you:
- **Measure real latency impact** of gateway migrations
- **Compare before/after performance** across environments  
- **Test multiple endpoint types** beyond simple health checks
- **Generate detailed reports** for stakeholders
- **Identify performance bottlenecks** in API gateways

## 🚨 Key Findings from Production Use

Testing revealed that gateway layers can add **significant latency**:
- Health-check endpoints: **Minimal impact** (~1-15ms)
- Authenticated endpoints: **Substantial impact** (60ms+ observed)
- **Real-world impact is 4x higher** than health-check estimates suggest

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-org/edge-front-door-latency-testing.git
cd edge-front-door-latency-testing

# Install dependencies
uv sync

# Install with optional auth dependencies (if needed for AWS)
uv sync --group auth

# Install with development dependencies (for testing/linting)
uv sync --group dev

# Make scripts executable
chmod +x *.sh *.py
```

## 🚀 Quick Start

### 1. Simple Health Check Test (No Auth Required)
```bash
uv run quick_latency_test.py
```

### 2. Enhanced Multi-Endpoint Test (Auth Required)
```bash
uv run enhanced_latency_test.py --environment prod --requests 20
```

### 3. Comprehensive Test Suite
```bash
./run_latency_test.sh --environment prod --requests 50
```

## 📊 Generate Reports

### CSV Reports (for Excel/Google Sheets)
```bash
uv run generate_csv_report.py
# Creates reports/ directory with multiple CSV files
```

### Excel Reports (formatted workbook)
```bash
uv run generate_excel_report.py
# Creates latency_analysis_report.xlsx
```

## 🛠️ Configuration

### Setting Up Your URLs

Edit the test scripts to configure your specific URLs:

```python
# In enhanced_latency_test.py or quick_latency_test.py
old_urls = {
    "dev": "https://api-direct.dev.example.com",
    "test": "https://api-direct.test.example.com", 
    "prod": "https://api-direct.example.com"
}

new_urls = {
    "dev": "https://api.gateway.dev.example.com",
    "test": "https://api.gateway.test.example.com",
    "prod": "https://api.gateway.example.com"
}
```

### Authentication Setup (Optional)

For authenticated endpoint testing:
1. Configure your authentication method in the test scripts
2. Set appropriate environment variables
3. Ensure proper API access credentials

Example for AWS SSO:
```bash
export SSO_DOMAIN="your-sso-domain.com"
aws sso login
```

## 📁 Project Structure

```
edge-front-door-latency-testing/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── pyproject.toml                      # Project configuration
├── LICENSE                             # MIT License
│
├── quick_latency_test.py               # Simple health-check testing
├── enhanced_latency_test.py            # Multi-endpoint testing with auth
├── run_latency_test.sh                 # Shell wrapper for comprehensive testing
│
├── generate_csv_report.py              # CSV report generator
├── generate_excel_report.py            # Excel report generator
│
├── README_LATENCY_TESTING.md           # Detailed technical documentation
├── manual_test_approach.md             # Manual testing alternatives
├── endpoint_comparison_analysis.md     # Why health-check testing isn't enough
│
└── comprehensive-tests/                # Advanced test suite
    ├── test_gateway_latency.py         # Full pytest-based framework
    └── README.md                       # Technical documentation
```

## 📈 Understanding Results

### Latency Metrics Explained

- **Mean**: Average response time across all requests
- **Median**: Middle value when response times are sorted
- **P95**: 95% of requests completed within this time
- **P99**: 99% of requests completed within this time

### Interpreting Gateway Impact

| Impact Level | Latency Increase | Recommendation |
|-------------|------------------|----------------|
| **Minimal** | < 10ms | ✅ Proceed with migration |
| **Low** | 10-25ms | ✅ Acceptable for most use cases |
| **Moderate** | 25-50ms | ⚠️ Evaluate based on SLA requirements |
| **High** | 50-100ms | ⚠️ Consider optimization or alternatives |
| **Critical** | > 100ms | 🚨 Requires immediate attention |

## 🎯 Best Practices

### 1. Test Multiple Endpoint Types
- ✅ **Health checks**: Baseline performance
- ✅ **Authenticated endpoints**: Real-world impact  
- ✅ **Data-heavy endpoints**: Payload size impact
- ✅ **External API calls**: End-to-end latency

### 2. Test Across Environments
- **Development**: Quick validation
- **Staging**: Pre-production testing
- **Production**: Real-world performance

### 3. Use Sufficient Sample Sizes
- **Minimum**: 10 requests per test
- **Recommended**: 20-50 requests
- **Statistical significance**: 100+ requests

### 4. Consider Time of Day
- Test during peak and off-peak hours
- Account for geographic distribution
- Monitor for consistency across time periods

## 🚨 Critical Warnings

### ⚠️ Health-Check Testing Limitations
**Health-check endpoints significantly underestimate real gateway impact.** Always test authenticated, realistic endpoints for production decisions.

### ⚠️ Authentication Required for Realistic Results
Most production APIs require authentication. Unauthenticated tests may miss critical latency sources.

### ⚠️ Network Conditions
Results vary based on:
- Geographic location
- Network quality
- Time of day
- Server load

## 📚 Documentation

- **README_LATENCY_TESTING.md**: Comprehensive setup and usage guide
- **manual_test_approach.md**: Alternative testing methods using curl
- **endpoint_comparison_analysis.md**: Technical analysis of endpoint differences

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test with your use case
5. Submit a pull request

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Open a GitHub issue
- **Documentation**: Check the docs/ directory
- **Examples**: See example configurations in test files

---

**Originally developed for Edge Front Door migration analysis**  
**Adaptable for any API gateway latency testing**

## 🏆 Success Stories

This toolkit has been successfully used to:
- ✅ Identify 60ms production latency increases
- ✅ Validate gateway performance across multiple environments  
- ✅ Generate stakeholder reports for migration decisions
- ✅ Prevent performance regressions in production

**Ready to test your gateway performance?** Start with `uv run quick_latency_test.py`!
