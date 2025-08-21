#!/usr/bin/env python3
"""Simple client example for the Sleeper MCP server.

This example shows how to integrate the MCP server with your own LLM application.
"""

import asyncio
import json
import httpx
from typing import Dict, Any, Optional


class SleeperMCPClient:
    """Simple client for the Sleeper MCP server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get available functions from the MCP server."""
        response = await self.client.get(f"{self.base_url}/capabilities")
        response.raise_for_status()
        return response.json()
    
    async def invoke_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a function on the MCP server."""
        payload = {
            "function_name": function_name,
            "parameters": parameters
        }
        
        response = await self.client.post(
            f"{self.base_url}/invoke",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def get_user(self, identifier: str) -> Dict[str, Any]:
        """Get user information."""
        return await self.invoke_function("get_user", {"identifier": identifier})
    
    async def get_user_leagues(self, user_id: str, season: str, sport: str = "nfl") -> Dict[str, Any]:
        """Get leagues for a user."""
        return await self.invoke_function("get_user_leagues", {
            "user_id": user_id,
            "season": season,
            "sport": sport
        })
    
    async def get_league(self, league_id: str) -> Dict[str, Any]:
        """Get league information."""
        return await self.invoke_function("get_league", {"league_id": league_id})
    
    async def get_league_rosters(self, league_id: str) -> Dict[str, Any]:
        """Get league rosters."""
        return await self.invoke_function("get_league_rosters", {"league_id": league_id})
    
    async def get_nfl_state(self) -> Dict[str, Any]:
        """Get NFL season state."""
        return await self.invoke_function("get_nfl_state", {})


async def main():
    """Example usage of the MCP client."""
    client = SleeperMCPClient()
    
    try:
        # Get available functions
        print("Available functions:")
        capabilities = await client.get_capabilities()
        for func in capabilities["functions"]:
            print(f"  - {func['name']}: {func['description']}")
        
        print("\n" + "="*50 + "\n")
        
        # Example: Get NFL state
        print("Getting NFL state...")
        nfl_state = await client.get_nfl_state()
        if nfl_state["status"] == "success":
            print("NFL State:", json.dumps(nfl_state["result"], indent=2))
        else:
            print("Error:", nfl_state["error"])
        
        print("\n" + "="*50 + "\n")
        
        # Example: Get user (replace with actual username)
        username = "example_user"  # Replace with actual username
        print(f"Getting user info for: {username}")
        user_info = await client.get_user(username)
        if user_info["status"] == "success":
            print("User Info:", json.dumps(user_info["result"], indent=2))
        else:
            print("Error:", user_info["error"])
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
