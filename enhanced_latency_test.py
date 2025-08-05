#!/usr/bin/env python3
"""
Enhanced latency test that includes real API endpoints with authentication.

This provides a more realistic assessment of Edge Front Door impact by testing
actual business endpoints rather than just health checks.

Usage:
    python enhanced_latency_test.py --environment dev --requests 20
"""
import asyncio
import time
import statistics
from typing import List, Dict, Any
import argparse

import httpx
from gd_auth.client import AwsIamAuthTokenClient
from mvci_logging import env, get_logger

logger = get_logger()


class EnhancedLatencyTest:
    """Enhanced latency testing with real API endpoints."""
    
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
        
        # Test data for real endpoints
        self.test_data = {
            "dev": {
                "customer_id": "00000000-0000-0000-0000-000000000000",
                "venture_id": "a4a93b88-da14-4532-a737-0712489bd017"
            },
            "test": {
                "customer_id": "00000000-0000-0000-0000-000000000000", 
                "venture_id": "a4a93b88-da14-4532-a737-0712489bd017"
            },
            "prod": {
                "customer_id": "00000000-0000-0000-0000-000000000000",
                "venture_id": "02c97c68-65ab-4805-9e46-22f13aae55e4"
            }
        }
    
    def get_test_endpoints(self) -> List[Dict[str, Any]]:
        """Get list of endpoints to test with their characteristics."""
        data = self.test_data.get(self.environment, self.test_data["dev"])
        
        return [
            {
                "name": "Health Check",
                "path": "/health-check",
                "auth_required": False,
                "expected_size": "tiny (~20B)",
                "processing": "minimal"
            },
            {
                "name": "Brands Status", 
                "path": f"/v1/customer/{data['customer_id']}/venture/{data['venture_id']}/inferred/brands/status",
                "auth_required": True,
                "expected_size": "small (~200B)",
                "processing": "moderate (auth + external call)"
            },
            {
                "name": "Brands Data",
                "path": f"/v1/customer/{data['customer_id']}/venture/{data['venture_id']}/inferred/brands", 
                "auth_required": True,
                "expected_size": "large (~2KB+)",
                "processing": "heavy (auth + external call + data processing)"
            },
            {
                "name": "Logo URL",
                "path": f"/v1/customer/{data['customer_id']}/venture/{data['venture_id']}/inferred/logo-url",
                "auth_required": True, 
                "expected_size": "small (~100B)",
                "processing": "moderate (auth + external call)"
            }
        ]
    
    async def test_endpoint(self, base_url: str, endpoint: Dict[str, Any], num_requests: int) -> Dict[str, Any]:
        """Test a specific endpoint."""
        name = endpoint["name"]
        path = endpoint["path"]
        auth_required = endpoint["auth_required"]
        
        print(f"\n🔬 Testing {name}")
        print(f"   Path: {path}")
        print(f"   Auth: {'Required' if auth_required else 'None'}")
        print(f"   Size: {endpoint['expected_size']}")
        print(f"   Processing: {endpoint['processing']}")
        
        headers = {}
        if auth_required:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        latencies = []
        status_codes = []
        response_sizes = []
        
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            # Warm up
            try:
                response = await client.get(f"{base_url}{path}", headers=headers)
                print(f"   Warmup: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  Warmup failed: {e}")
                return {
                    "name": name,
                    "error": f"Warmup failed: {e}",
                    "latencies": [],
                    "status_codes": [],
                    "response_sizes": []
                }
            
            # Run tests
            for i in range(num_requests):
                start_time = time.perf_counter()
                try:
                    response = await client.get(f"{base_url}{path}", headers=headers)
                    end_time = time.perf_counter()
                    
                    latency_ms = (end_time - start_time) * 1000
                    latencies.append(latency_ms)
                    status_codes.append(response.status_code)
                    response_sizes.append(len(response.content))
                    
                    print(f"   Request {i+1:2d}: {latency_ms:6.1f}ms (HTTP {response.status_code}, {len(response.content):4d}B)")
                    
                except Exception as e:
                    print(f"   Request {i+1:2d}: Failed - {e}")
                
                await asyncio.sleep(0.1)  # Small delay
        
        return {
            "name": name,
            "path": path, 
            "auth_required": auth_required,
            "latencies": latencies,
            "status_codes": status_codes,
            "response_sizes": response_sizes,
            "expected_size": endpoint["expected_size"],
            "processing": endpoint["processing"]
        }
    
    async def run_comparison(self, num_requests: int = 10):
        """Run latency comparison across all endpoints."""
        old_url = self.old_urls.get(self.environment)
        new_url = self.new_urls.get(self.environment)
        
        if not old_url or not new_url:
            print(f"❌ Unknown environment: {self.environment}")
            return
        
        print(f"🚀 Enhanced Latency Test - {self.environment.upper()} Environment")
        print("=" * 70)
        print(f"Old URL: {old_url}")
        print(f"New URL: {new_url}")
        print(f"Requests per endpoint: {num_requests}")
        
        endpoints = self.get_test_endpoints()
        results = []
        
        for endpoint in endpoints:
            print(f"\n{'='*50}")
            print(f"ENDPOINT: {endpoint['name']}")
            print(f"{'='*50}")
            
            # Test old URL
            print(f"\n📊 Testing OLD URL...")
            old_result = await self.test_endpoint(old_url, endpoint, num_requests)
            
            # Test new URL  
            print(f"\n📊 Testing NEW URL...")
            new_result = await self.test_endpoint(new_url, endpoint, num_requests)
            
            # Calculate comparison
            comparison = self.compare_results(old_result, new_result)
            results.append(comparison)
            
            # Show immediate results
            self.print_endpoint_summary(comparison)
        
        # Final summary
        self.print_final_summary(results)
        return results
    
    def compare_results(self, old_result: Dict[str, Any], new_result: Dict[str, Any]) -> Dict[str, Any]:
        """Compare results between old and new endpoints."""
        if "error" in old_result or "error" in new_result:
            return {
                "name": old_result.get("name", "Unknown"),
                "old_error": old_result.get("error"),
                "new_error": new_result.get("error")
            }
        
        old_latencies = old_result["latencies"]
        new_latencies = new_result["latencies"]
        
        if not old_latencies or not new_latencies:
            return {
                "name": old_result["name"],
                "error": "No successful requests"
            }
        
        old_avg = statistics.mean(old_latencies)
        new_avg = statistics.mean(new_latencies)
        additional_latency = new_avg - old_avg
        percent_increase = (additional_latency / old_avg) * 100 if old_avg > 0 else 0
        
        return {
            "name": old_result["name"],
            "path": old_result["path"],
            "auth_required": old_result["auth_required"],
            "expected_size": old_result["expected_size"],
            "processing": old_result["processing"],
            "old_avg": old_avg,
            "new_avg": new_avg,
            "additional_latency": additional_latency,
            "percent_increase": percent_increase,
            "old_count": len(old_latencies),
            "new_count": len(new_latencies),
            "avg_response_size": statistics.mean(new_result["response_sizes"]) if new_result["response_sizes"] else 0
        }
    
    def print_endpoint_summary(self, comparison: Dict[str, Any]):
        """Print summary for a single endpoint."""
        if "error" in comparison:
            print(f"\n❌ {comparison['name']}: {comparison.get('error', 'Unknown error')}")
            return
        
        name = comparison["name"]
        additional = comparison["additional_latency"]
        percent = comparison["percent_increase"]
        
        print(f"\n📊 {name} Results:")
        print(f"   Old latency: {comparison['old_avg']:.1f}ms")
        print(f"   New latency: {comparison['new_avg']:.1f}ms")
        print(f"   Additional:  {additional:+.1f}ms ({percent:+.1f}%)")
        print(f"   Avg size:    {comparison['avg_response_size']:.0f} bytes")
        
        if additional < 5:
            print(f"   Status: ✅ Excellent")
        elif additional < 15:
            print(f"   Status: ✅ Good") 
        elif additional < 30:
            print(f"   Status: ⚠️  Fair")
        else:
            print(f"   Status: ❌ Concerning")
    
    def print_final_summary(self, results: List[Dict[str, Any]]):
        """Print final summary of all endpoints."""
        print(f"\n{'='*70}")
        print("FINAL SUMMARY")
        print(f"{'='*70}")
        
        valid_results = [r for r in results if "error" not in r]
        
        if not valid_results:
            print("❌ No valid results to summarize")
            return
        
        print(f"{'Endpoint':<20} {'Old (ms)':<10} {'New (ms)':<10} {'Additional':<12} {'% Change':<10}")
        print("-" * 70)
        
        total_additional = 0
        for result in valid_results:
            name = result["name"][:18]
            old_avg = result["old_avg"]
            new_avg = result["new_avg"] 
            additional = result["additional_latency"]
            percent = result["percent_increase"]
            
            print(f"{name:<20} {old_avg:<10.1f} {new_avg:<10.1f} {additional:+8.1f}ms {percent:+7.1f}%")
            total_additional += additional
        
        avg_additional = total_additional / len(valid_results)
        print("-" * 70)
        print(f"{'AVERAGE':<20} {'':<10} {'':<10} {avg_additional:+8.1f}ms")
        
        print(f"\n🎯 Key Insights:")
        print(f"   • Health check may not represent real performance")
        print(f"   • Authenticated endpoints show different characteristics")
        print(f"   • Larger responses may have different gateway overhead") 
        print(f"   • Average additional latency: {avg_additional:+.1f}ms")


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Enhanced Edge Front Door latency testing")
    parser.add_argument("--environment", "-e", default="dev", choices=["dev", "test", "prod"],
                       help="Environment to test (default: dev)")
    parser.add_argument("--requests", "-r", type=int, default=10,
                       help="Number of requests per endpoint (default: 10)")
    
    args = parser.parse_args()
    
    # Get auth token
    try:
        client = AwsIamAuthTokenClient(sso_host=env.SSO_GODADDY_DOMAIN)
        auth_token = client.token
        print(f"✅ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("💡 Make sure you're logged in via SSO")
        return
    
    # Run enhanced test
    tester = EnhancedLatencyTest(args.environment, auth_token)
    await tester.run_comparison(args.requests)


if __name__ == "__main__":
    asyncio.run(main())
