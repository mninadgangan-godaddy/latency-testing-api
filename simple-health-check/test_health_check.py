#!/usr/bin/env python3
"""
Simple health check latency comparison tool.

Compares latency between old direct endpoints and new Edge Front Door endpoints
for health check endpoints only.

Usage:
    python test_health_check.py --environment dev --requests 50
"""
import asyncio
import statistics
import time
import argparse
import os
import httpx


class SimpleHealthCheckTest:
    """Simple health check latency tester."""
    
    def __init__(self, environment: str):
        self.environment = environment
        self.auth_token = os.getenv('AUTH_TOKEN', '')
        
        # URL mappings for different environments
        self.old_urls = {
            "dev": "https://venture.mvciapi.dev.aws.gdcld.net",
            "test": "https://venture.mvciapi.stage.aws.gdcld.net", 
            "prod": "https://venture.mvciapi.prod.aws.gdcld.net"
        }
        
        self.new_urls = {
            "dev": "https://venture-profile-api.frontdoor.dev-godaddy.com",
            "test": "https://venture-profile-api.frontdoor.test-godaddy.com",  # Updated test domain
            "prod": "https://venture-profile-api.frontdoor.godaddy.com"
        }
    
    async def measure_latency(self, url: str) -> float:
        """Measure latency for a single request."""
        headers = {}
        if self.auth_token and self.auth_token.strip():
            headers["Authorization"] = f"sso-jwt {self.auth_token}"
            
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                end_time = time.time()
                
                # Check if request was successful
                if response.status_code >= 400:
                    print(f"  Warning: {url} returned status {response.status_code}")
                    return None
                    
                return (end_time - start_time) * 1000  # Convert to milliseconds
        except Exception as e:
            print(f"  Error requesting {url}: {e}")
            return None
    
    async def run_test(self, num_requests: int) -> dict:
        """Run latency test for health check endpoints."""
        old_url = f"{self.old_urls[self.environment]}/health-check"
        new_url = f"{self.new_urls[self.environment]}/health-check"
        
        print(f"Testing {self.environment} environment health check latency...")
        print(f"Old endpoint: {old_url}")
        print(f"New endpoint: {new_url}")
        print(f"Running {num_requests} requests to each endpoint...")
        
        if self.auth_token:
            print("Using AUTH_TOKEN for authentication")
        else:
            print("Running without authentication (set AUTH_TOKEN env var if needed)")
        
        # Quick connectivity test
        print("\nTesting connectivity...")
        test_old = await self.measure_latency(old_url)
        test_new = await self.measure_latency(new_url)
        
        if test_old is None and test_new is None:
            print("❌ Both endpoints appear to be unreachable or require authentication")
            print("💡 Try running with AUTH_TOKEN environment variable if authentication is required")
        elif test_old is None:
            print("⚠️  Old endpoint appears to be unreachable")
        elif test_new is None:
            print("⚠️  New endpoint appears to be unreachable")
        else:
            print("✅ Both endpoints are reachable")
        print()
        
        # Test old endpoint
        print("Testing old endpoint...")
        old_latencies = []
        for i in range(num_requests):
            latency = await self.measure_latency(old_url)
            if latency is not None:
                old_latencies.append(latency)
            if (i + 1) % 10 == 0:
                print(f"  Completed {i + 1}/{num_requests} requests")
        
        # Test new endpoint
        print("Testing new endpoint...")
        new_latencies = []
        for i in range(num_requests):
            latency = await self.measure_latency(new_url)
            if latency is not None:
                new_latencies.append(latency)
            if (i + 1) % 10 == 0:
                print(f"  Completed {i + 1}/{num_requests} requests")
        
        return {
            'old_latencies': old_latencies,
            'new_latencies': new_latencies,
            'old_url': old_url,
            'new_url': new_url
        }
    
    def analyze_results(self, results: dict) -> None:
        """Analyze and display results."""
        old_latencies = results['old_latencies']
        new_latencies = results['new_latencies']
        
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
        
        # Display results
        print("\n" + "="*70)
        print("HEALTH CHECK LATENCY COMPARISON")
        print("="*70)
        print(f"Environment: {self.environment}")
        print(f"Old endpoint: {results['old_url']}")
        print(f"New endpoint: {results['new_url']}")
        print(f"Successful requests: {len(old_latencies)} old, {len(new_latencies)} new")
        print()
        
        print(f"{'Metric':<10} {'Old (ms)':<12} {'New (ms)':<12} {'Difference (ms)':<15} {'% Change':<10}")
        print("-" * 70)
        
        for metric in ['mean', 'median', 'p95', 'p99']:
            old_val = old_stats[metric]
            new_val = new_stats[metric]
            diff = new_val - old_val
            pct_change = (diff / old_val) * 100 if old_val > 0 else 0
            
            print(f"{metric.upper():<10} {old_val:<12.2f} {new_val:<12.2f} {diff:<15.2f} {pct_change:<10.1f}%")
        
        # Summary
        mean_diff = new_stats['mean'] - old_stats['mean']
        if mean_diff < 0:
            print(f"\n📊 Summary: Gateway is {abs(mean_diff):.2f}ms faster on average")
        else:
            print(f"\n📊 Summary: Gateway adds {mean_diff:.2f}ms additional latency on average")
    
    def _percentile(self, data: list, percentile: int) -> float:
        """Calculate percentile of a dataset."""
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        lower = int(index)
        upper = min(lower + 1, len(sorted_data) - 1)
        weight = index - lower
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Simple health check latency comparison")
    parser.add_argument("--environment", "-e", default="dev", 
                       choices=["dev", "test", "prod"],
                       help="Environment to test (default: dev)")
    parser.add_argument("--requests", "-r", type=int, default=30,
                       help="Number of requests per endpoint (default: 30)")
    
    args = parser.parse_args()
    
    tester = SimpleHealthCheckTest(args.environment)
    results = await tester.run_test(args.requests)
    tester.analyze_results(results)


if __name__ == "__main__":
    asyncio.run(main())
