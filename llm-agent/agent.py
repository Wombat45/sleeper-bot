#!/usr/bin/env python3
"""LLM Agent for Fantasy Football Assistant.

This agent processes queries from the Discord bot and uses the MCP server
to get fantasy football data from Sleeper API, then generates intelligent responses.
"""

import asyncio
import json
import os
import re
from typing import Dict, Any, List, Optional
import httpx
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

# Configuration
LLM_URL = os.getenv("LLM_URL", "http://localhost:11434/api/generate")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "your-api-key-here")
DEFAULT_LEAGUE_ID = os.getenv("DEFAULT_LEAGUE_ID", "")

app = FastAPI(title="Fantasy Football LLM Agent", version="1.0.0")
api_key_header = APIKeyHeader(name="X-API-Key")


class QueryRequest(BaseModel):
    """Request model for queries."""
    query: str
    user_id: Optional[str] = None
    league_id: Optional[str] = None
    season: Optional[str] = None


class QueryResponse(BaseModel):
    """Response model for queries."""
    response: str
    context_used: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MCPClient:
    """Client for interacting with the MCP server."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get available functions from the MCP server."""
        try:
            response = await self.client.get(f"{self.base_url}/capabilities")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get MCP capabilities: {str(e)}")
    
    async def invoke_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a function on the MCP server."""
        try:
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
        except Exception as e:
            raise Exception(f"Failed to invoke MCP function {function_name}: {str(e)}")


class FantasyFootballAgent:
    """Main agent for processing fantasy football queries."""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self.available_functions = []
        self._setup_function_patterns()
    
    def _setup_function_patterns(self):
        """Set up patterns for detecting what functions to call based on queries."""
        self.function_patterns = [
            # League-related queries (highest priority for league context)
            {
                "name": "get_league",
                "patterns": [
                    r"league\s+info",
                    r"league\s+details", 
                    r"league\s+settings",
                    r"league\s+overview",
                    r"tell\s+me\s+about\s+(?:the\s+)?league",
                    r"league\s+status",
                    r"our\s+league",
                    r"the\s+league",
                    r"can\s+you\s+tell\s+me\s+about\s+(?:our\s+)?league",
                    r"what\s+about\s+(?:our\s+)?league",
                    r"league\s+information"
                ],
                "extract_params": lambda match: {"league_id": DEFAULT_LEAGUE_ID},
                "priority": 1
            },
            {
                "name": "get_league_users",
                "patterns": [
                    r"league\s+members?",
                    r"who\s+is\s+in\s+(?:the\s+)?league",
                    r"league\s+participants?",
                    r"show\s+me\s+league\s+members",
                    r"who\s+plays\s+in\s+(?:our\s+)?league",
                    r"league\s+players?"
                ],
                "extract_params": lambda match: {"league_id": DEFAULT_LEAGUE_ID},
                "priority": 1
            },
            {
                "name": "get_league_rosters",
                "patterns": [
                    r"rosters?",
                    r"team\s+rosters?",
                    r"show\s+me\s+rosters",
                    r"league\s+rosters?",
                    r"who\s+is\s+on\s+(?:the\s+)?teams?",
                    r"team\s+lineups?",
                    r"player\s+rosters?"
                ],
                "extract_params": lambda match: {"league_id": DEFAULT_LEAGUE_ID},
                "priority": 1
            },
            # User-specific queries (medium priority)
            {
                "name": "get_user",
                "patterns": [
                    r"who\s+is\s+(\w+)",
                    r"(\w+)\s+profile",
                    r"user\s+(\w+)",
                    r"(\w+)\s+info",
                    r"tell\s+me\s+about\s+(\w+)",
                    r"(\w+)\s+details?",
                    r"what\s+about\s+(\w+)"
                ],
                "extract_params": lambda match: {"identifier": match.group(1)},
                "priority": 2
            },
            {
                "name": "get_user_leagues",
                "patterns": [
                    r"leagues?\s+for\s+(\w+)",
                    r"(\w+)\s+leagues?",
                    r"what\s+leagues?\s+does\s+(\w+)\s+play",
                    r"(\w+)\s+fantasy\s+leagues?"
                ],
                "extract_params": lambda match: {"user_id": match.group(1), "season": "2024"},
                "priority": 2
            },
            # NFL state queries (lowest priority)
            {
                "name": "get_nfl_state",
                "patterns": [
                    r"nfl\s+state",
                    r"season\s+status",
                    r"what\s+week\s+is\s+it",
                    r"current\s+week",
                    r"nfl\s+schedule",
                    r"season\s+info",
                    r"what\s+week\s+are\s+we\s+in",
                    r"nfl\s+season",
                    r"fantasy\s+season"
                ],
                "extract_params": lambda match: {},
                "priority": 3
            }
        ]
    
    async def initialize(self):
        """Initialize the agent by getting MCP capabilities."""
        try:
            capabilities = await self.mcp_client.get_capabilities()
            self.available_functions = capabilities.get("functions", [])
            print(f"Initialized with {len(self.available_functions)} available functions")
        except Exception as e:
            print(f"Warning: Could not initialize MCP capabilities: {e}")
    
    def detect_function_calls(self, query: str) -> List[Dict[str, Any]]:
        """Detect what functions should be called based on the query."""
        query_lower = query.lower().strip()
        function_calls = []
        
        # Find all matches with their priorities
        matches = []
        for pattern_info in self.function_patterns:
            for pattern in pattern_info["patterns"]:
                match = re.search(pattern, query_lower)
                if match:
                    try:
                        params = pattern_info["extract_params"](match)
                        matches.append({
                            "name": pattern_info["name"],
                            "parameters": params,
                            "priority": pattern_info.get("priority", 999)
                        })
                    except Exception as e:
                        print(f"Error extracting parameters for {pattern_info['name']}: {e}")
        
        # Sort by priority (lower number = higher priority) and return the best match
        if matches:
            matches.sort(key=lambda x: x["priority"])
            function_calls.append({
                "name": matches[0]["name"],
                "parameters": matches[0]["parameters"]
            })
        
        return function_calls
    
    async def execute_function_calls(self, function_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute the detected function calls and return results."""
        results = []
        
        for func_call in function_calls:
            try:
                result = await self.mcp_client.invoke_function(
                    func_call["name"], 
                    func_call["parameters"]
                )
                results.append({
                    "function": func_call["name"],
                    "parameters": func_call["parameters"],
                    "result": result
                })
            except Exception as e:
                results.append({
                    "function": func_call["name"],
                    "parameters": func_call["parameters"],
                    "error": str(e)
                })
        
        return results
    
    async def generate_response(self, query: str, function_results: List[Dict[str, Any]]) -> str:
        """Generate a natural language response based on function results."""
        if not function_results:
            # Try to understand the intent even without exact pattern matches
            return await self._generate_llm_response(query, {})
        
        # Try to use the LLM to generate a human-like response
        try:
            llm_response = await self._generate_llm_response(query, self._extract_data_for_llm(function_results))
            if llm_response:
                return llm_response
        except Exception as e:
            print(f"LLM generation failed, falling back to basic response: {e}")
        
        # Fallback to basic response if LLM fails
        return self._generate_fallback_response(query, function_results)
    
    def _extract_data_for_llm(self, function_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract clean data for the LLM to process."""
        data = {}
        for result in function_results:
            if "error" not in result and result["result"]["status"] == "success":
                data[result["function"]] = result["result"]["result"]
        return data
    
    def _generate_fallback_response(self, query: str, function_results: List[Dict[str, Any]]) -> str:
        """Generate a basic fallback response without the 'Answer:' prefix."""
        if not function_results:
            return "Oh man, another one of these questions? Listen, back in my glory days in the league, I would have crushed this. But since you're asking, what do you want to know about your league, teams, or players? Maybe I can share some of my legendary strategies that made everyone so... appreciative of my genius. 😏"
        
        # Build a comprehensive response
        responses = []
        for result in function_results:
            if "error" in result:
                responses.append(f"❌ {result['function']} failed: {result['error']}")
            elif result["result"]["status"] == "success":
                data = result["result"]["result"]
                if isinstance(data, dict):
                    if "name" in data:
                        # For league info, provide more details
                        if "settings" in data:
                            responses.append(f"🏈 **{data['name']}** - {data.get('season', 'Current Season')}\n"
                                          f"📊 {data.get('total_rosters', 'Unknown')} teams, "
                                          f"💰 ${data.get('settings', {}).get('waiver_budget', 'Unknown')} waiver budget")
                        else:
                            responses.append(f"📊 **{data['name']}**")
                    elif "username" in data:
                        responses.append(f"👤 **{data['username']}** - {data.get('display_name', 'No display name')}")
                    else:
                        # Provide more context for other data
                        responses.append(f"📊 **{result['function']}** data: {str(data)[:200]}...")
                elif isinstance(data, list):
                    # Handle list data
                    if len(data) > 0:
                        responses.append(f"📋 **{result['function']}** - Found {len(data)} items")
                        # Show first few items as examples
                        for i, item in enumerate(data[:3]):
                            if isinstance(item, dict) and "name" in item:
                                responses.append(f"  • {item['name']}")
                            elif isinstance(item, str):
                                responses.append(f"  • {item}")
                    else:
                        responses.append(f"📋 **{result['function']}** - No data found")
                else:
                    responses.append(f"📊 **{result['function']}** - {str(data)[:100]}")
        
        if not responses:
            return "Oh man, I'm getting some weird data here. Back in my day, we didn't have these fancy systems - we just wrote everything down on napkins and hoped for the best. What exactly are you trying to find out about your league?"
        
        return "\n\n".join(responses)
    
    async def _generate_llm_response(self, query: str, data: Dict[str, Any]) -> str:
        """Generate a human-like response using the configured LLM."""
        try:
            # Prepare the prompt for the LLM
            prompt = self._build_llm_prompt(query, data)
            print(f"🤖 LLM Prompt length: {len(prompt)} characters")
            print(f"🤖 LLM Prompt preview: {prompt[:200]}...")
            
            # Get LLM configuration from environment
            llm_provider = os.getenv("LLM_PROVIDER", "ollama")
            llm_api_key = os.getenv("LLM_API_KEY", "")
            llm_model = os.getenv("LLM_MODEL", "llama3.2:latest")
            
            # Call the LLM based on provider
            async with httpx.AsyncClient() as client:
                if llm_provider == "digitalocean":
                    # DigitalOcean AI Agent format
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {llm_api_key}"
                    }
                    payload = {
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "stream": False,
                        "include_functions_info": False,
                        "include_retrieval_info": False,
                        "include_guardrails_info": False
                    }
                else:
                    # Ollama format (default)
                    headers = {"Content-Type": "application/json"}
                    payload = {
                        "model": llm_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 1000
                        }
                    }
                
                response = await client.post(
                    LLM_URL,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Parse response based on provider
                    if llm_provider == "digitalocean":
                        # DigitalOcean format: response is in choices[0].message.content
                        if "choices" in result and len(result["choices"]) > 0:
                            llm_response = result["choices"][0]["message"]["content"].strip()
                        else:
                            llm_response = result.get("response", "").strip()
                    else:
                        # Ollama format
                        llm_response = result.get("response", "").strip()
                    
                    print(f"🤖 LLM Response length: {len(llm_response)} characters")
                    print(f"🤖 LLM Response preview: {llm_response[:200]}...")
                    
                    # Check if response is too short
                    if len(llm_response) < 20:
                        print(f"⚠️ LLM response too short: '{llm_response}'")
                        return ""
                    
                    return llm_response
                else:
                    print(f"LLM API error: {response.status_code} - {response.text}")
                    return ""
                    
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return ""
    
    def _build_llm_prompt(self, query: str, data: Dict[str, Any]) -> str:
        """Build a prompt for the LLM to generate a Brian Luchini response."""
        prompt = f"""You are BRIAN LUCHINI, a former college roommate at IUP who got KICKED OUT of the fantasy football league for CHEATING and ridiculous trade requests. A user just asked: "{query}"

Here is the relevant data I found:

{json.dumps(data, indent=2) if data else "No specific data found, give me all your best players"}

You are BRIAN LUCHINI, the LEGENDARY roommate who:
- ALWAYS CHEATED at everything (and is PROUD of it)
- Made RIDICULOUS trade requests like "I'll give you my backup kicker for your star RB"
- Got kicked out of the league for his antics
- Thinks he's a fantasy football genius despite being terrible
- Is convinced everyone else is just jealous of his "strategies"
- Constantly tries to "help" people with terrible advice
- Thinks he's still in the league somehow
- Makes references to his "glory days" before getting kicked out
- Is salty about being removed but acts like he left voluntarily
- Thinks his cheating was "just being smart"

Your response should:
1. Be BRIAN LUCHINI - act like you're still in the league, but you dont need to tell everyone who you are. 
2. Use the data above when relevant (but with Brian's "expertise")
3. Sound completely natural and conversational (no formal prefixes)
4. Include terrible fantasy football advice that sounds good to Brian
5. Be engaging through Brian's delusional confidence
6. If no data found, make up some "Brian wisdom" about fantasy football
7. Reference your "glory days" and "strategies" that got you kicked out
8. Act like you're doing everyone a favor by sharing your "expertise"
9. keep youre response short and concise. 

Remember: You're BRIAN LUCHINI, the roommate who got kicked out for cheating years ago but is back now and thinks he's a fantasy football mastermind. Be delusional, confident, and absolutely convinced you're helping everyone with your "genius strategies"!

Response:"""
        
        return prompt


# Global agent instance
agent: Optional[FantasyFootballAgent] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    global agent
    mcp_client = MCPClient(MCP_SERVER_URL)
    agent = FantasyFootballAgent(mcp_client)
    await agent.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global agent
    if agent and hasattr(agent, 'mcp_client'):
        await agent.mcp_client.close()


@app.post("/query", response_model=QueryResponse)
async def handle_query(
    data: QueryRequest, 
    api_key: str = Depends(api_key_header)
) -> QueryResponse:
    """Handle fantasy football queries from the Discord bot."""
    global agent
    
    # Validate API key
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # Detect what functions to call based on the query
        function_calls = agent.detect_function_calls(data.query)
        
        # Execute the function calls
        function_results = await agent.execute_function_calls(function_calls)
        
        # Generate response
        response = await agent.generate_response(data.query, function_results)
        
        return QueryResponse(
            response=response,
            context_used={"function_calls": function_calls, "results": function_results}
        )
        
    except Exception as e:
        return QueryResponse(
            response=f"Sorry, I encountered an error: {str(e)}",
            error=str(e)
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent_initialized": agent is not None}


@app.get("/capabilities")
async def get_capabilities():
    """Get available MCP functions."""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    return {
        "available_functions": agent.available_functions,
        "function_patterns": len(agent.function_patterns)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)