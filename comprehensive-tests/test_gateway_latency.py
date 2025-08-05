"""
Latency testing script to measure the additional latency introduced by Edge Front Door gateway.

This script compares response times between:
- Old direct endpoints (e.g., https://venture.mvciapi.dev.aws.gdcld.net)
- New gateway endpoints (e.g., https://venture-profile-api.frontdoor.dev-godaddy.com)

Usage:
    python test_gateway_latency.py --environment dev --requests 50
"""
import asyncio
import statistics
import time
from typing import Any, Dict, List, Optional, Tuple
import argparse
import json
from datetime import datetime

import httpx
from gd_auth.client import AwsIamAuthTokenClient
from mvci_logging import env, get_logger

logger = get_logger()


class LatencyTester:
    """Test latency between old and new endpoints."""
    
    def __init__(self, environment: str, auth_token: str):
        self.environment = environment
        self.auth_token = auth_token
        
        # URL mappings
        self.old_urls = {
            "dev": "https://venture.mvciapi.dev.aws.gdcld.net",
            "test": "https://venture.mvciapi.stage.aws.gdcld.net",
            "prod": "https://venture.mvciapi.prod.aws.gdcld.net"
        }
        
        self.new_urls = {
            "dev": "https://venture-profile-api.frontdoor.dev-godaddy.com",
            "test": "https://venture-profile-api.frontdoor.test-godaddy.com", 
            "prod": "https://venture-profile-api.frontdoor.godaddy.com"
        }
        
        # Test endpoints to measure - using environment-specific data
        if self.environment == "prod":
            venture_id = "02c97c68-65ab-4805-9e46-22f13aae55e4"
        else:
            venture_id = "a4a93b88-da14-4532-a737-0712489bd017"
        
        customer_id = "00000000-0000-0000-0000-000000000000"
        
        self.test_endpoints = [
            "/health-check",  # Baseline: Simple endpoint (no auth, minimal processing)
            f"/v1/customer/{customer_id}/venture/{venture_id}/inferred/brands/status",  # Moderate: Auth + external call
            f"/v1/customer/{customer_id}/venture/{venture_id}/inferred/logo-url",  # Moderate: Auth + external call  
        ]
        
    def get_urls(self) -> Tuple[str, str]:
        """Get old and new URLs for the current environment."""
        old_url = self.old_urls.get(self.environment)
        new_url = self.new_urls.get(self.environment)
        
        if not old_url or not new_url:
            raise ValueError(f"Unknown environment: {self.environment}")
            
        return old_url, new_url
    
    async def measure_request_latency(self, client: httpx.AsyncClient, url: str) -> Optional[float]:
        """Measure the latency of a single request."""
        start_time = time.perf_counter()
        try:
            response = await client.get(url, timeout=10.0)
            end_time = time.perf_counter()
            
            # Only measure successful requests or known client errors (4xx)
            if response.status_code < 500:
                return (end_time - start_time) * 1000  # Convert to milliseconds
            else:
                logger.warning(f"Server error {response.status_code} for {url}")
                return None
        except Exception as e:
            logger.warning(f"Request failed for {url}: {e}")
            return None
    
    async def run_latency_test(self, base_url: str, endpoint: str, num_requests: int) -> List[float]:
        """Run multiple requests to measure latency distribution."""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        async with httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            logger.info(f"Testing {base_url}{endpoint} with {num_requests} requests...")
            
            # Warm up with a few requests
            for _ in range(3):
                await self.measure_request_latency(client, endpoint)
                await asyncio.sleep(0.1)
            
            # Collect latency measurements
            latencies = []
            for i in range(num_requests):
                latency = await self.measure_request_latency(client, endpoint)
                if latency is not None:
                    latencies.append(latency)
                
                # Small delay between requests to avoid overwhelming the server
                if i < num_requests - 1:
                    await asyncio.sleep(0.05)
            
            return latencies
    
    async def compare_latencies(self, endpoint: str, num_requests: int) -> Dict[str, Any]:
        """Compare latencies between old and new endpoints."""
        old_url, new_url = self.get_urls()
        
        logger.info(f"Comparing latencies for endpoint: {endpoint}")
        logger.info(f"Old URL: {old_url}")
        logger.info(f"New URL: {new_url}")
        
        # Run tests concurrently
        old_latencies, new_latencies = await asyncio.gather(
            self.run_latency_test(old_url, endpoint, num_requests),
            self.run_latency_test(new_url, endpoint, num_requests)
        )
        
        # Calculate statistics
        def calculate_stats(latencies: List[float]) -> Dict[str, Any]:
            if not latencies:
                return {"error": "No successful requests"}
            
            return {
                "count": len(latencies),
                "mean": statistics.mean(latencies),
                "median": statistics.median(latencies),
                "min": min(latencies),
                "max": max(latencies),
                "std_dev": statistics.stdev(latencies) if len(latencies) > 1 else 0,
                "p95": self._percentile(latencies, 95),
                "p99": self._percentile(latencies, 99)
            }
        
        old_stats = calculate_stats(old_latencies)
        new_stats = calculate_stats(new_latencies)
        
        # Calculate additional latency
        additional_latency: Dict[str, float] = {}
        if "error" not in old_stats and "error" not in new_stats:
            additional_latency = {
                "mean": new_stats["mean"] - old_stats["mean"],
                "median": new_stats["median"] - old_stats["median"],
                "p95": new_stats["p95"] - old_stats["p95"],
                "p99": new_stats["p99"] - old_stats["p99"]
            }
        
        return {
            "endpoint": endpoint,
            "old_url": old_url,
            "new_url": new_url,
            "old_stats": old_stats,
            "new_stats": new_stats,
            "additional_latency_ms": additional_latency,
            "raw_data": {
                "old_latencies": old_latencies,
                "new_latencies": new_latencies
            }
        }
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate the nth percentile of a dataset."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_data) - 1)
        weight = index - lower_index
        return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight


def print_results(results: List[Dict[str, Any]]):
    """Print formatted results."""
    print("\n" + "="*80)
    print("EDGE FRONT DOOR LATENCY ANALYSIS")
    print("="*80)
    
    for result in results:
        endpoint = result["endpoint"]
        print(f"\nEndpoint: {endpoint}")
        print("-" * 60)
        
        if "error" in result["old_stats"] or "error" in result["new_stats"]:
            print(f"❌ Error in testing: {result.get('old_stats', {}).get('error', '')} {result.get('new_stats', {}).get('error', '')}")
            continue
        
        old_stats = result["old_stats"]
        new_stats = result["new_stats"]
        additional = result["additional_latency_ms"]
        
        print(f"Old URL: {result['old_url']}")
        print(f"New URL: {result['new_url']}")
        print()
        
        # Latency comparison table
        print(f"{'Metric':<15} {'Old (ms)':<12} {'New (ms)':<12} {'Additional (ms)':<15} {'% Increase':<12}")
        print("-" * 70)
        
        metrics = ['mean', 'median', 'p95', 'p99']
        for metric in metrics:
            old_val = old_stats[metric]
            new_val = new_stats[metric]
            additional_val = additional[metric]
            percent_increase = (additional_val / old_val * 100) if old_val > 0 else 0
            
            print(f"{metric.upper():<15} {old_val:<12.2f} {new_val:<12.2f} {additional_val:<15.2f} {percent_increase:<12.1f}%")
        
        print()
        print(f"Successful requests: {old_stats['count']} old, {new_stats['count']} new")
        
        # Summary
        avg_additional = additional['mean']
        if avg_additional > 0:
            print(f"📊 Average additional latency: +{avg_additional:.2f}ms ({avg_additional/old_stats['mean']*100:.1f}% increase)")
        else:
            print(f"📊 Average latency difference: {avg_additional:.2f}ms (gateway is faster)")


async def main():
    """Main function to run latency tests."""
    parser = argparse.ArgumentParser(description="Test Edge Front Door latency impact")
    parser.add_argument("--environment", "-e", default="dev", choices=["dev", "test", "prod"],
                       help="Environment to test (default: dev)")
    parser.add_argument("--requests", "-r", type=int, default=30,
                       help="Number of requests per endpoint (default: 30)")
    parser.add_argument("--output", "-o", help="Output file for detailed results (JSON)")
    
    args = parser.parse_args()
    
    # Set up authentication
    try:
        client = AwsIamAuthTokenClient(sso_host=env.SSO_GODADDY_DOMAIN)
        auth_token = client.token
    except Exception as e:
        logger.error(f"Failed to get auth token: {e}")
        return
    
    # Initialize tester
    tester = LatencyTester(args.environment, auth_token)
    
    print(f"Starting latency analysis for {args.environment} environment...")
    print(f"Testing {args.requests} requests per endpoint")
    
    # Run tests for all endpoints
    results = []
    for endpoint in tester.test_endpoints:
        try:
            result = await tester.compare_latencies(endpoint, args.requests)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to test endpoint {endpoint}: {e}")
            results.append({
                "endpoint": endpoint,
                "error": str(e)
            })
    
    # Print results
    print_results(results)
    
    # Save detailed results if requested
    if args.output:
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "environment": args.environment,
            "num_requests": args.requests,
            "results": results
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nDetailed results saved to: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
