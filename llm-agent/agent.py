# llm-agent/agent.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
import requests
import os

app = FastAPI()
LLM_URL = "http://localhost:11434/api/generate"
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

@app.post("/query")
async def handle_query(data: dict, api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    query = data.get("query")
    context = ""
    if "standings" in query.lower():
        mcp_response = requests.get(
            f"{MCP_SERVER_URL}/get_league_standings/your_league_id",
            headers={"X-API-Key": API_KEY}
        ).json()
        context = f"League standings: {mcp_response}"
    # Add more: "rosters" -> /get_league_rosters, etc.
    prompt = f"{context}\nAnswer: {query}" if context else query
    llm_response = requests.post(LLM_URL, json={"model": "llama3", "prompt": prompt}).json()
    return {"response": llm_response["response"]}