#!/usr/bin/env python3
"""Advanced LLM integration example for the Sleeper MCP server.

This example shows how to integrate the MCP server with function calling
in your LLM application, including tool definitions and response handling.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# This would be your actual LLM client - replace with your implementation
# from your_llm_client import LLMClient, Tool, ToolCall


@dataclass
class Tool:
    """Tool definition for function calling."""
    name: str
    description: str
    parameters: Dict[str, Any]


@dataclass
class ToolCall:
    """Tool call from the LLM."""
    name: str
    arguments: Dict[str, Any]


class MockLLMClient:
    """Mock LLM client for demonstration purposes.
    
    Replace this with your actual LLM client implementation.
    """
    
    def __init__(self):
        self.tools: List[Tool] = []
    
    def add_tool(self, tool: Tool):
        """Add a tool to the LLM client."""
        self.tools.append(tool)
    
    async def chat_with_tools(self, message: str) -> List[ToolCall]:
        """Simulate LLM chat with tool calling.
        
        In a real implementation, this would send the message to your LLM
        and return the tool calls it wants to make.
        """
        print(f"LLM received: {message}")
        print("Available tools:")
        for tool in self.tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Simulate LLM deciding to call a tool
        # In reality, your LLM would analyze the message and decide what tools to call
        if "user" in message.lower():
            return [ToolCall("get_user", {"identifier": "example_user"})]
        elif "league" in message.lower():
            return [ToolCall("get_user_leagues", {"user_id": "123", "season": "2024"})]
        elif "nfl" in message.lower():
            return [ToolCall("get_nfl_state", {})]
        else:
            return []


class SleeperMCPClient:
    """Client for the Sleeper MCP server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        import httpx
        self.client = httpx.AsyncClient()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
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


class FantasyFootballAssistant:
    """Fantasy football assistant that integrates LLM with MCP server."""
    
    def __init__(self, llm_client: MockLLMClient, mcp_client: SleeperMCPClient):
        self.llm_client = llm_client
        self.mcp_client = mcp_client
        self._setup_tools()
    
    def _setup_tools(self):
        """Set up the available tools for the LLM."""
        # These tool definitions would be sent to your LLM
        tools = [
            Tool(
                name="get_user",
                description="Get information about a Sleeper user by username or user ID",
                parameters={
                    "type": "object",
                    "properties": {
                        "identifier": {
                            "type": "string",
                            "description": "Username or user ID of the user to look up"
                        }
                    },
                    "required": ["identifier"]
                }
            ),
            Tool(
                name="get_user_leagues",
                description="Get all leagues for a specific user in a given season",
                parameters={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID to look up leagues for"
                        },
                        "season": {
                            "type": "string",
                            "description": "Season year (e.g., '2024')"
                        },
                        "sport": {
                            "type": "string",
                            "description": "Sport type (default: 'nfl')",
                            "default": "nfl"
                        }
                    },
                    "required": ["user_id", "season"]
                }
            ),
            Tool(
                name="get_league",
                description="Get detailed information about a specific league",
                parameters={
                    "type": "object",
                    "properties": {
                        "league_id": {
                            "type": "string",
                            "description": "League ID to look up"
                        }
                    },
                    "required": ["league_id"]
                }
            ),
            Tool(
                name="get_league_rosters",
                description="Get all rosters in a specific league",
                parameters={
                    "type": "object",
                    "properties": {
                        "league_id": {
                            "type": "string",
                            "description": "League ID to look up rosters for"
                        }
                    },
                    "required": ["league_id"]
                }
            ),
            Tool(
                name="get_nfl_state",
                description="Get current NFL season state information",
                parameters={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
        
        # Add tools to the LLM client
        for tool in tools:
            self.llm_client.add_tool(tool)
    
    async def chat(self, message: str) -> str:
        """Chat with the fantasy football assistant."""
        print(f"\nUser: {message}")
        
        # Get tool calls from the LLM
        tool_calls = await self.llm_client.chat_with_tools(message)
        
        if not tool_calls:
            return "I can help you with fantasy football questions! Try asking about users, leagues, rosters, or NFL state."
        
        # Execute the tool calls
        results = []
        for tool_call in tool_calls:
            print(f"\nExecuting tool: {tool_call.name} with args: {tool_call.arguments}")
            
            try:
                result = await self.mcp_client.invoke_function(
                    tool_call.name, 
                    tool_call.arguments
                )
                
                if result["status"] == "success":
                    results.append(f"✅ {tool_call.name}: {json.dumps(result['result'], indent=2)}")
                else:
                    results.append(f"❌ {tool_call.name} failed: {result['error']}")
                    
            except Exception as e:
                results.append(f"❌ {tool_call.name} error: {str(e)}")
        
        # In a real implementation, you would send the results back to your LLM
        # for it to generate a natural language response
        response = f"I found some information for you:\n\n" + "\n\n".join(results)
        
        print(f"\nAssistant: {response}")
        return response


async def main():
    """Example usage of the fantasy football assistant."""
    llm_client = MockLLMClient()
    
    async with SleeperMCPClient() as mcp_client:
        assistant = FantasyFootballAssistant(llm_client, mcp_client)
        
        # Example conversations
        await assistant.chat("What's the current NFL state?")
        await assistant.chat("Get information about user 'example_user'")
        await assistant.chat("Show me the leagues for user 123 in the 2024 season")


if __name__ == "__main__":
    asyncio.run(main())
