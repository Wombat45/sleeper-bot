# llm-agent/Dockerfile
FROM ollama/ollama
RUN ollama pull llama3
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY agent.py .
EXPOSE 11434 8000
CMD ["sh", "-c", "ollama serve & uvicorn agent:app --host 0.0.0.0 --port 8000"]