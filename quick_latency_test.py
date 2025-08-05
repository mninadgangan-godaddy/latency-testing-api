#!/usr/bin/env python3
"""
Quick latency test script for Edge Front Door impact analysis.

This is a simplified version for quick testing without requiring the full test framework.
Run this directly to get a quick assessment of latency differences.

Usage:
    python quick_latency_test.py
"""
import asyncio
import time
import statistics
from typing import List, Optional
import httpx


class QuickLatencyTest:
    """Simple latency tester for quick assessment."""
    
    def __init__(self):
        # URL mappings - you can modify these as needed
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
    
    async def measure_latency(self, url: str, num_requests: int = 10) -> List[float]:
        """Measure latency for a given URL."""
        print(f"Testing {url}...")
        
        latencies = []
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Warm up
            try:
                await client.get(f"{url}/health-check")
            except:
                print(f"  ⚠️  Could not reach {url} - this might be expected if auth is required")
                return []
            
            # Measure latencies
            for i in range(num_requests):
                start_time = time.perf_counter()
                try:
                    response = await client.get(f"{url}/health-check")
                    end_time = time.perf_counter()
                    
                    if response.status_code < 500:  # Accept 2xx, 3xx, 4xx
                        latency_ms = (end_time - start_time) * 1000
                        latencies.append(latency_ms)
                        print(f"  Request {i+1}: {latency_ms:.1f}ms (HTTP {response.status_code})")
                    else:
                        print(f"  Request {i+1}: Server error {response.status_code}")
                        
                except Exception as e:
                    print(f"  Request {i+1}: Failed - {e}")
                
                # Small delay between requests
                await asyncio.sleep(0.1)
        
        return latencies
    
    async def compare_environments(self, environment: str = "dev", num_requests: int = 10):
        """Compare latencies between old and new URLs for a given environment."""
        print(f"\n🚀 Testing {environment} environment with {num_requests} requests each")
        print("=" * 70)
        
        old_url = self.old_urls.get(environment)
        new_url = self.new_urls.get(environment)
        
        if not old_url or not new_url:
            print(f"❌ Unknown environment: {environment}")
            return
        
        # Test both URLs
        old_latencies = await self.measure_latency(old_url, num_requests)
        new_latencies = await self.measure_latency(new_url, num_requests)
        
        # Calculate and display results
        print(f"\n📊 Results for {environment} environment:")
        print("-" * 50)
        
        if not old_latencies and not new_latencies:
            print("❌ No successful requests to either endpoint")
            return
        elif not old_latencies:
            print("❌ No successful requests to old endpoint")
            return
        elif not new_latencies:
            print("❌ No successful requests to new endpoint")
            return
        
        # Calculate statistics
        old_avg = statistics.mean(old_latencies)
        new_avg = statistics.mean(new_latencies)
        additional_latency = new_avg - old_avg
        percent_increase = (additional_latency / old_avg) * 100
        
        print(f"Old URL average:     {old_avg:.1f}ms")
        print(f"New URL average:     {new_avg:.1f}ms")
        print(f"Additional latency:  {additional_latency:+.1f}ms ({percent_increase:+.1f}%)")
        
        # Performance assessment
        if additional_latency < 5:
            print("✅ Excellent: Very low additional latency")
        elif additional_latency < 15:
            print("✅ Good: Acceptable additional latency")
        elif additional_latency < 30:
            print("⚠️  Fair: Moderate additional latency")
        else:
            print("⚠️  Concerning: High additional latency")
        
        # Additional statistics if we have enough data
        if len(old_latencies) > 3 and len(new_latencies) > 3:
            old_p95 = self._percentile(old_latencies, 95)
            new_p95 = self._percentile(new_latencies, 95)
            print(f"P95 latency:         {old_p95:.1f}ms → {new_p95:.1f}ms ({new_p95-old_p95:+.1f}ms)")
        
        print()
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile."""
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_data) - 1)
        weight = index - lower_index
        return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight


async def main():
    """Run quick latency tests."""
    print("🔬 Quick Edge Front Door Latency Test")
    print("=" * 50)
    print("This script tests the /health-check endpoint without authentication.")
    print("For comprehensive testing with authentication, use the full test suite.")
    print()
    
    tester = QuickLatencyTest()
    
    # Test all environments
    for env in ["dev", "test", "prod"]:
        try:
            await tester.compare_environments(env, num_requests=15)
        except Exception as e:
            print(f"❌ Error testing {env}: {e}")
    
    print("✅ Quick latency test completed!")
    print()
    print("💡 For more comprehensive testing:")
    print("   ./run_latency_test.sh --environment dev --requests 50")


if __name__ == "__main__":
    asyncio.run(main())
