# Edge Front Door Latency Testing Suite

A comprehensive toolkit for measuring the latency impact of API gateway migrations, specifically designed for testing Edge Front Door performance.

## 🚨 Key Finding

Production testing revealed that Edge Front Door adds **~60ms (28% increase)** - significantly higher than simple health-check estimates suggest.

## 📁 Directory Structure

```
edge-front-door-latency-testing/
├── README.md                           # This file
├── quick_latency_test.py               # Simple health-check testing (no auth)
├── enhanced_latency_test.py            # Multi-endpoint testing with authentication
├── run_latency_test.sh                 # Shell wrapper for comprehensive testing
├── generate_csv_report.py              # CSV report generator
├── generate_excel_report.py            # Excel report generator
├── README_LATENCY_TESTING.md           # Comprehensive documentation
├── manual_test_approach.md             # Manual testing guide
├── endpoint_comparison_analysis.md     # Analysis of endpoint differences
└── comprehensive-tests/                # Advanced test suite
    ├── test_gateway_latency.py         # Full test framework
    └── README.md                       # Technical documentation
```

## 🚀 Quick Start

### Option 1: Simple Health Check Test (No Auth Required)
```bash
python quick_latency_test.py
```

### Option 2: Enhanced Multi-Endpoint Test (Auth Required)
```bash
python enhanced_latency_test.py --environment prod --requests 20
```

### Option 3: Comprehensive Test Suite
```bash
./run_latency_test.sh --environment prod --requests 50
```

## 📊 Generate Reports

### CSV Reports (for Excel/Google Sheets)
```bash
python generate_csv_report.py
# Creates reports/ directory with multiple CSV files
```

### Excel Reports (formatted workbook)
```bash
python generate_excel_report.py
# Creates latency_analysis_report.xlsx
```

## 🎯 Example Usage

Configure your URLs in the test scripts:

```python
# Old direct URLs
old_urls = {
    "dev": "https://api.example.dev.com",
    "test": "https://api.example.test.com", 
    "prod": "https://api.example.com"
}

# New gateway URLs  
new_urls = {
    "dev": "https://api.gateway.dev.com",
    "test": "https://api.gateway.test.com",
    "prod": "https://api.gateway.com"
}
```

## 📈 Current Test Results

| Environment | Additional Latency | % Increase | Status |
|-------------|-------------------|------------|---------|
| **dev** | -1.2ms ⬇️ | -0.6% | ✅ Excellent (health-check only) |
| **test** | +8.8ms ⬆️ | +4.3% | ✅ Good (health-check only) |
| **prod** | **+60ms ⬆️** | **+28%** | ⚠️ **Significant impact detected** |

⚠️ **Important**: Initial dev/test results were health-check endpoint only. Production results show the real gateway impact.

## 🔧 Setup

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Or using the project setup
pip install -e .
```

### Authentication (Optional)
For authenticated endpoint testing:
1. Configure your authentication method in the test scripts
2. Set appropriate environment variables
3. Ensure proper API access credentials

## 📚 Documentation

- **README_LATENCY_TESTING.md**: Complete setup and usage guide
- **manual_test_approach.md**: Alternative testing methods
- **endpoint_comparison_analysis.md**: Why health-check testing is insufficient

## 🎯 Recommendations

1. **✅ Immediate**: Use production results for migration decisions
2. **🔧 Short-term**: Fix authentication to test dev/test environments
3. **📊 Ongoing**: Set up regular monitoring with these tools
4. **⚠️ Important**: Consider the 60ms production impact in migration planning

## 🚨 Critical Notes

- **Health-check testing alone is insufficient** - it underestimates real impact by 75%+
- **Authentication required** for realistic endpoint testing
- **Production shows significant latency increase** - validate before full migration
- **Test multiple endpoint types** for comprehensive assessment

---

**Generated**: December 2024  
**Contact**: Engineering Team  
**Purpose**: Edge Front Door migration latency analysis
