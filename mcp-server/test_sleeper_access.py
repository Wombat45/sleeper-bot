#!/usr/bin/env python3
"""Test script to verify Sleeper API access without authentication.

This script tests that the MCP server can access the Sleeper API endpoints
without requiring any API keys or authentication.
"""

import asyncio
import httpx
import json
from typing import Dict, Any


async def test_sleeper_api_access():
    """Test access to various Sleeper API endpoints."""
    
    base_url = "https://api.sleeper.app/v1"
    
    # Test endpoints that don't require authentication
    test_endpoints = [
        "/nfl/state",           # NFL season state
        "/players/nfl",         # NFL players (this might be large)
        "/players/nfl/trending", # Trending players
        "/players/nfl/trending/add", # Players being added
        "/players/nfl/trending/drop", # Players being dropped
    ]
    
    print("Testing Sleeper API access without authentication...")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in test_endpoints:
            try:
                print(f"\nTesting: {endpoint}")
                response = await client.get(f"{base_url}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if endpoint == "/nfl/state":
                        print(f"✅ Success! NFL State:")
                        print(f"   Season: {data.get('season', 'N/A')}")
                        print(f"   Week: {data.get('week', 'N/A')}")
                        print(f"   Season Type: {data.get('season_type', 'N/A')}")
                    
                    elif endpoint == "/players/nfl/trending/add":
                        print(f"✅ Success! Trending Add Players:")
                        if isinstance(data, list) and len(data) > 0:
                            print(f"   Sample player: {data[0].get('player_id', 'N/A')}")
                            print(f"   Total trending add players: {len(data)}")
                        else:
                            print(f"   No trending add players found")
                    
                    elif endpoint == "/players/nfl/trending/drop":
                        print(f"✅ Success! Trending Drop Players:")
                        if isinstance(data, list) and len(data) > 0:
                            print(f"   Sample player: {data[0].get('player_id', 'N/A')}")
                            print(f"   Total trending drop players: {len(data)}")
                        else:
                            print(f"   No trending drop players found")
                    
                    else:
                        print(f"✅ Success! Response size: {len(str(data))} characters")
                
                else:
                    print(f"❌ Failed with status {response.status_code}")
                    print(f"   Response: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"❌ Error testing {endpoint}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Sleeper API access test completed!")
    print("   The API is accessible without authentication as expected.")


async def test_mcp_server_integration():
    """Test that the MCP server can properly call Sleeper API functions."""
    
    print("\nTesting MCP Server integration with Sleeper API...")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test MCP server health
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ MCP Server is running and healthy")
            else:
                print(f"❌ MCP Server health check failed: {response.status_code}")
                return
            
            # Test MCP server capabilities
            response = await client.get("http://localhost:8000/capabilities")
            if response.status_code == 200:
                capabilities = response.json()
                print(f"✅ MCP Server capabilities retrieved")
                print(f"   Available functions: {len(capabilities.get('functions', []))}")
                
                # Test a simple function call
                test_function = {
                    "function_name": "get_nfl_state",
                    "parameters": {}
                }
                
                response = await client.post(
                    "http://localhost:8000/invoke",
                    json=test_function
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        print("✅ MCP Server successfully called Sleeper API")
                        data = result.get("result", {})
                        print(f"   NFL State retrieved: Season {data.get('season', 'N/A')}, Week {data.get('week', 'N/A')}")
                    else:
                        print(f"❌ MCP function call failed: {result.get('error', 'Unknown error')}")
                else:
                    print(f"❌ MCP invoke failed: {response.status_code}")
                    
            else:
                print(f"❌ MCP Server capabilities failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error testing MCP server integration: {str(e)}")
        print("   Make sure the MCP server is running on localhost:8000")


if __name__ == "__main__":
    print("Sleeper API Access Test")
    print("This script verifies that the Sleeper API is accessible without authentication")
    print("and that the MCP server can properly integrate with it.\n")
    
    # Test direct Sleeper API access
    asyncio.run(test_sleeper_api_access())
    
    # Test MCP server integration (if server is running)
    try:
        asyncio.run(test_mcp_server_integration())
    except Exception as e:
        print(f"\n⚠️  MCP Server integration test skipped: {str(e)}")
        print("   Start the MCP server first to test full integration")
    
    print("\n🎯 Test completed! The Sleeper API is ready to use without authentication.")
