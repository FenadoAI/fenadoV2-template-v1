# Project Setup

## Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload
```

### Required Environment
- `MONGO_URL`: MongoDB connection string
- `DB_NAME`: Database name
- `LITELLM_AUTH_TOKEN`, `LITELLM_BASE_URL`, `AI_MODEL_NAME`: LiteLLM configuration
- Optional: `CODEXHUB_MCP_AUTH_TOKEN` for MCP tool access

### Running the API Tests
Unit tests mock external services and use FastAPI's `TestClient`:
```bash
cd backend
pytest
```
Integration smoke scripts that hit live services were removed; reach for manual calls when you need them.

## Frontend  
```bash
cd frontend
bun install
bun start
```

## Environment

### Backend Environment Variables
Create `backend/.env` with:
- `MONGO_URL`: MongoDB connection string
- `DB_NAME`: Database name
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `CODEXHUB_MCP_AUTH_TOKEN`: Authentication token for MCP services (web search, image generation)
- `LITELLM_AUTH_TOKEN`: Authentication token for LiteLLM API
- `LITELLM_BASE_URL`: LiteLLM API base URL (default: https://litellm-docker-545630944929.us-central1.run.app)
- `AI_MODEL_NAME`: AI model to use (default: gemini-2.5-pro)

### Frontend Environment Variables
- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8000)
- For production: Set to your deployed backend URL (e.g., https://api.yourdomain.com)

## AI Agents

This project includes extensible AI agents built with **LangGraph** and **MCP (Model Context Protocol)**:

### Available Agents

1. **SearchAgent** - Web search and research with real-time information
   - Uses web search MCP tools
   - Verifies tool usage to prevent fabricated responses
   - Ideal for current events, weather, news

2. **ImageAgent** - Image generation from text prompts
   - Generates real images via CodexHub Image MCP
   - HTTP verification ensures images are accessible
   - Returns persistent Google Cloud Storage URLs

3. **ChatAgent** - General conversation and assistance
4. **BaseAgent** - Base class for creating custom agents

### Usage Examples

#### Image Generation
```python
from ai_agents import ImageAgent, AgentConfig
import asyncio

async def generate_image():
    config = AgentConfig()
    agent = ImageAgent(config)
    
    response = await agent.execute(
        "Generate an image of a sunset over mountains",
        use_tools=True
    )
    
    if response.success and response.metadata.get('tools_used'):
        print(response.content)  # Real GCS URL
        # https://storage.googleapis.com/fenado-ai-farm-public/generated/{uuid}.webp

asyncio.run(generate_image())
```

#### Web Search
```python
from ai_agents import SearchAgent, AgentConfig
import asyncio

async def search_web():
    config = AgentConfig()
    agent = SearchAgent(config)
    
    response = await agent.execute(
        "Use web search to find today's weather in Tokyo",
        use_tools=True
    )
    
    if response.success and response.metadata.get('tools_used'):
        print(response.content)  # Real-time search results

asyncio.run(search_web())
```

### Documentation

- 📖 [Image Agent Documentation](docs/image-agent.md) - Complete guide to image generation
- 📖 [LangGraph + MCP Integration](backend/LANGGRAPH_MCP_INTEGRATION.md) - Technical guide
- 📖 [AI Agent Architecture](docs/aiagent.md) - Agent system architecture
- 📖 [Tech Stack](docs/techstack.md) - Technology stack overview

## Test
```bash
# Test AI agents (includes SearchAgent and ImageAgent)
cd backend && python tests/test_agents.py

# Test backend API (if server is running)
cd backend && python tests/test_api.py
```

### Expected Test Results

```
📊 Test Summary:
  Search Agent:           ✅ PASSED
  Image Agent:            ✅ PASSED
  Structured Output:      ✅ PASSED

🎉 All AI Agents tests passed!
✅ MCP tools are properly invoked (not fabricated)
✅ Structured JSON output working correctly
✅ Images verified from Google Cloud Storage
```

**What the tests verify:**
- ✅ MCP tools are actually invoked (`tools_used: True`)
- ✅ Real web search results (not from training data)
- ✅ Real image URLs from Google Cloud Storage
- ✅ HTTP 200 verification for image accessibility
- ✅ Structured JSON output with Pydantic validation
