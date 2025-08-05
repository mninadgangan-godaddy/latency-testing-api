#!/usr/bin/env python3
"""
Custom endpoint latency testing tool.

Compares latency between old direct endpoints and new Edge Front Door endpoints
for custom business endpoints with configurable customer and venture IDs.

Usage:
    python test_custom_endpoints.py --environment dev --customer-id 12345 --venture-id abcdef --requests 30
"""
import asyncio
import statistics
import time
import argparse
import os
import httpx


class CustomEndpointTest:
    """Custom endpoint latency tester with configurable IDs."""
    
    def __init__(self, environment: str, customer_id: str, venture_id: str):
        self.environment = environment
        self.customer_id = customer_id
        self.venture_id = venture_id
        self.auth_token = os.getenv('AUTH_TOKEN', '')
        
        # URL mappings for different environments
        self.old_urls = {
            "dev": "https://venture.mvciapi.dev.aws.gdcld.net",
            "test": "https://venture.mvciapi.stage.aws.gdcld.net",
            "prod": "https://venture.mvciapi.prod.aws.gdcld.net"
        }
        
        self.new_urls = {
            "dev": "https://venture-profile-api.frontdoor.dev-godaddy.com",
            "test": "https://venture-profile-api.frontdoor.stage-godaddy.com",
            "prod": "https://venture-profile-api.frontdoor.godaddy.com"
        }
        
        # Test endpoints with placeholder IDs
        self.test_endpoints = [
            f"/v1/customer/{self.customer_id}/venture/{self.venture_id}/inferred/brands/status",
            f"/v1/customer/{self.customer_id}/venture/{self.venture_id}/inferred/logo-url",
            f"/v1/customer/{self.customer_id}/venture/{self.venture_id}/profile"
        ]
    
    async def measure_latency(self, url: str) -> float:
        """Measure latency for a single request."""
        headers = {}
        if self.auth_token and self.auth_token.strip():
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                end_time = time.time()
                return (end_time - start_time) * 1000  # Convert to milliseconds
        except Exception:
            return None
    
    async def test_endpoint(self, endpoint: str, num_requests: int) -> dict:
        """Test a specific endpoint with both old and new URLs."""
        old_url = f"{self.old_urls[self.environment]}{endpoint}"
        new_url = f"{self.new_urls[self.environment]}{endpoint}"
        
        print(f"\nTesting endpoint: {endpoint}")
        print(f"Old URL: {old_url}")
        print(f"New URL: {new_url}")
        
        # Test old endpoint
        print(f"Testing old endpoint with {num_requests} requests...")
        old_latencies = []
        for i in range(num_requests):
            latency = await self.measure_latency(old_url)
            if latency is not None:
                old_latencies.append(latency)
        
        # Test new endpoint  
        print(f"Testing new endpoint with {num_requests} requests...")
        new_latencies = []
        for i in range(num_requests):
            latency = await self.measure_latency(new_url)
            if latency is not None:
                new_latencies.append(latency)
        
        return {
            'endpoint': endpoint,
            'old_latencies': old_latencies,
            'new_latencies': new_latencies,
            'old_url': old_url,
            'new_url': new_url
        }
    
    async def run_all_tests(self, num_requests: int) -> list:
        """Run tests for all configured endpoints."""
        print(f"Starting latency analysis for {self.environment} environment...")
        print(f"Customer ID: {self.customer_id}")
        print(f"Venture ID: {self.venture_id}")
        print(f"Testing {num_requests} requests per endpoint")
        
        if self.auth_token:
            print("Using AUTH_TOKEN for authentication")
        else:
            print("Running without authentication (set AUTH_TOKEN env var if needed)")
        
        results = []
        for endpoint in self.test_endpoints:
            result = await self.test_endpoint(endpoint, num_requests)
            results.append(result)
        
        return results
    
    def analyze_results(self, results: list) -> None:
        """Analyze and display results for all endpoints."""
        print("\n" + "="*80)
        print("CUSTOM ENDPOINT LATENCY ANALYSIS")
        print("="*80)
        
        for result in results:
            self._analyze_single_result(result)
    
    def _analyze_single_result(self, result: dict) -> None:
        """Analyze results for a single endpoint."""
        old_latencies = result['old_latencies']
        new_latencies = result['new_latencies']
        
        print(f"\nEndpoint: {result['endpoint']}")
        print("-" * 60)
        print(f"Old URL: {result['old_url']}")
        print(f"New URL: {result['new_url']}")
        
        if not old_latencies or not new_latencies:
            print("❌ Error: No successful requests to analyze")
            return
        
        # Calculate statistics
        old_stats = {
            'mean': statistics.mean(old_latencies),
            'median': statistics.median(old_latencies),
            'p95': self._percentile(old_latencies, 95),
            'p99': self._percentile(old_latencies, 99)
        }
        
        new_stats = {
            'mean': statistics.mean(new_latencies),
            'median': statistics.median(new_latencies),
            'p95': self._percentile(new_latencies, 95),
            'p99': self._percentile(new_latencies, 99)
        }
        
        print(f"\n{'Metric':<10} {'Old (ms)':<12} {'New (ms)':<12} {'Additional (ms)':<15} {'% Increase':<10}")
        print("-" * 70)
        
        for metric in ['mean', 'median', 'p95', 'p99']:
            old_val = old_stats[metric]
            new_val = new_stats[metric]
            diff = new_val - old_val
            pct_change = (diff / old_val) * 100 if old_val > 0 else 0
            
            print(f"{metric.upper():<10} {old_val:<12.2f} {new_val:<12.2f} {diff:<15.2f} {pct_change:<10.1f}%")
        
        print(f"\nSuccessful requests: {len(old_latencies)} old, {len(new_latencies)} new")
        
        # Summary
        mean_diff = new_stats['mean'] - old_stats['mean']
        if mean_diff < 0:
            print(f"📊 Average latency difference: {mean_diff:.2f}ms (gateway is faster)")
        else:
            print(f"📊 Average additional latency: +{mean_diff:.2f}ms ({(mean_diff/old_stats['mean']*100):.1f}% increase)")
    
    def _percentile(self, data: list, percentile: int) -> float:
        """Calculate percentile of a dataset."""
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        lower = int(index)
        upper = min(lower + 1, len(sorted_data) - 1)
        weight = index - lower
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Custom endpoint latency testing")
    parser.add_argument("--environment", "-e", default="dev",
                       choices=["dev", "test", "prod"],
                       help="Environment to test (default: dev)")
    parser.add_argument("--customer-id", "-c", required=True,
                       help="Customer ID for API endpoints")
    parser.add_argument("--venture-id", "-v", required=True,
                       help="Venture ID for API endpoints")
    parser.add_argument("--requests", "-r", type=int, default=30,
                       help="Number of requests per endpoint (default: 30)")
    parser.add_argument("--endpoints", nargs="+",
                       help="Custom endpoints to test (optional, will use defaults if not provided)")
    
    args = parser.parse_args()
    
    tester = CustomEndpointTest(args.environment, args.customer_id, args.venture_id)
    
    # Allow custom endpoints if provided
    if args.endpoints:
        # Replace placeholders in custom endpoints
        custom_endpoints = []
        for endpoint in args.endpoints:
            endpoint = endpoint.replace("{customer_id}", args.customer_id)
            endpoint = endpoint.replace("{venture_id}", args.venture_id)
            custom_endpoints.append(endpoint)
        tester.test_endpoints = custom_endpoints
    
    async def run_tests():
        results = await tester.run_all_tests(args.requests)
        tester.analyze_results(results)
    
    asyncio.run(run_tests())


if __name__ == "__main__":
    main()
