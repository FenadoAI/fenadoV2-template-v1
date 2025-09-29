# Image Generation Agent Documentation

## Overview

The `ImageAgent` is an extensible AI agent built with **LangGraph** and **MCP (Model Context Protocol)** that generates real images from text prompts. It uses LangGraph's `create_react_agent` to properly invoke MCP tools and verify image generation.

## Setup

### Prerequisites

1. **CODEXHUB_MCP_AUTH_TOKEN**: Required for accessing the image generation MCP service
2. **LITELLM_AUTH_TOKEN**: Required for LLM API access  
3. **LangGraph**: For agent orchestration (`langgraph>=0.6.7`)
4. **LangChain MCP Adapters**: For MCP integration (`langchain-mcp-adapters>=0.1.9`)
5. **Python Dependencies**: See `backend/requirements.txt`

### Environment Variables

```bash
# In backend/.env
CODEXHUB_MCP_AUTH_TOKEN=your_codexhub_token_here
LITELLM_AUTH_TOKEN=your_litellm_token_here
LITELLM_BASE_URL=https://litellm-docker-545630944929.us-central1.run.app
AI_MODEL_NAME=gemini-2.5-pro
```

## Usage

### Basic Example

```python
import asyncio
from ai_agents import ImageAgent, AgentConfig

async def generate_image():
    # Create agent configuration
    config = AgentConfig()
    
    # Initialize image agent
    image_agent = ImageAgent(config)
    
    # Generate image from prompt
    response = await image_agent.execute(
        "Generate an image of a sunset over mountains",
        use_tools=True
    )
    
    if response.success:
        print(response.content)
    else:
        print(f"Error: {response.error}")

# Run
asyncio.run(generate_image())
```

## Response Format

The `ImageAgent` returns a single high-quality image in markdown format via the CodexHub Image MCP. The response includes:
- A descriptive alt text
- A direct URL to the generated image hosted on Google Cloud Storage
- URLs are persistent and do not expire (unlike temporary signed URLs)

### Example Response

```markdown
https://storage.googleapis.com/fenado-ai-farm-public/generated/fccb3f99-7763-4f09-87ff-ca01f6b72cc8.webp
```

Or with description:

```markdown
![Image of a sunset over mountains](https://storage.googleapis.com/fenado-ai-farm-public/generated/2c385c97-c286-4f12-94cb-0cb305efec87.webp)
```

**Important Notes:**
- URLs are **persistent** and hosted on Google Cloud Storage
- Images are stored with unique UUIDs for identification  
- Current format: `https://storage.googleapis.com/fenado-ai-farm-public/generated/{uuid}.webp`
- No expiration - URLs remain accessible long-term
- Generated via CodexHub Image MCP service
- **LangGraph ensures tools are actually invoked** (not fabricated by LLM)

## Extracting Image URLs

To extract image URLs from the response:

```python
import re

response = await image_agent.execute("Generate an image of a cat", use_tools=True)

if response.success:
    # Extract all URLs from the response
    urls = re.findall(r'https?://[^\s\)]+', response.content)
    
    print(f"Generated {len(urls)} images:")
    for i, url in enumerate(urls, 1):
        print(f"{i}. {url}")
```

### Example Output

```
Generated 1 image:
1. https://storage.googleapis.com/fenado-ai-farm-public/generated/fccb3f99-7763-4f09-87ff-ca01f6b72cc8.webp
```

## Testing

Run the test suite to verify image generation is working:

```bash
cd backend
python tests/test_agents.py
```

The test will:
- ✅ Initialize the ImageAgent with proper configuration
- ✅ Connect to the image generation MCP server
- ✅ Generate images from a test prompt
- ✅ Extract and display image URLs
- ✅ Validate the response format

### Expected Test Output

```
🧪 Image Agent Test
==============================
LiteLLM Token: sk-ZeGnbno...
Model: gemini-2.5-pro
LiteLLM Base URL: https://litellm-docker-545630944929.us-central1.run.app

🎨 Prompt: Generate an image of a sunset over mountains
Generating image...

✅ Success: True
ℹ️  Metadata: {'model': 'gemini-2.5-pro', 'tools_available': 1, 'tools_used': True, 'message_count': 5}
ℹ️  MCP Tools Available: 1
ℹ️  MCP Tools Actually Used: True

📝 Full Response:
https://storage.googleapis.com/fenado-ai-farm-public/generated/fccb3f99-7763-4f09-87ff-ca01f6b72cc8.webp

🖼️  Image URLs found:
   1. https://storage.googleapis.com/fenado-ai-farm-public/generated/fccb3f99-7763-4f09-87ff-ca01f6b72cc8.webp
      ✅ Valid Google Cloud Storage URL

🔍 Verifying image URL accessibility...
   HTTP Status: 200
   ✅ Image URL is accessible (HTTP 200)

🎯 CORRECT: MCP tools were used and real image generated!
   ✅ Image URL verified: https://storage.googleapis.com/fenado-ai-farm-public/generated/fccb3f99-7763-4f09-87ff-ca01f6b72cc8.webp
```

## Architecture

### Class Structure

```python
class ImageAgent(BaseAgent):
    """Image generation agent with LangGraph and MCP support"""
    
    def __init__(self, config: AgentConfig):
        # Specialized system prompt for image generation
        system_prompt = """You are an AI assistant specialized in generating images...
        You MUST use the available image generation tools to create images.
        NEVER fabricate or make up image URLs."""
        super().__init__(config, system_prompt)
        
        # Setup image MCP
        self._mcp_setup_done = False
    
    async def setup_image_mcp(self):
        # Connect to CodexHub Image MCP endpoint asynchronously
        server_configs = {
            "image-generation": {
                "transport": "streamable_http",  # Critical: Use streamable_http
                "url": "https://mcp.codexhub.ai/image/mcp",
                "headers": {"x-team-key": mcp_token}
            }
        }
        await self.setup_mcp(server_configs)
```

### LangGraph Integration

The agent uses **LangGraph's `create_react_agent`** for tool orchestration:

```python
from langgraph.prebuilt import create_react_agent

# Create agent with MCP tools
agent = create_react_agent(llm, mcp_tools)

# Execute with messages
result = await agent.ainvoke({
    "messages": [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ]
})

# Verify tools were actually used
tools_called = any(
    hasattr(msg, "tool_calls") and msg.tool_calls 
    for msg in result["messages"]
)
```

### MCP Integration

The ImageAgent connects to the CodexHub Image MCP service:
- **Endpoint**: `https://mcp.codexhub.ai/image/mcp`
- **Transport**: `streamable_http` (NOT "http" or "type")
- **Authentication**: Uses `x-team-key` header with `CODEXHUB_MCP_AUTH_TOKEN`
- **Tool Loading**: Async `await client.get_tools()`
- **Verification**: HTTP status check confirms real images

## Best Practices

1. **Prompt Engineering**: Be descriptive in your prompts for better results
   - ✅ Good: "A photorealistic image of a sunset over snow-capped mountains with a lake in the foreground"
   - ❌ Poor: "sunset"

2. **Error Handling**: Always check `response.success` before processing
   ```python
   if response.success:
       # Process images
   else:
       print(f"Error: {response.error}")
   ```

3. **✅ Verify Tool Usage**: Always check that MCP tools were actually invoked
   ```python
   tools_used = response.metadata.get('tools_used', False)
   if not tools_used:
       print("Warning: LLM may have fabricated the response!")
   ```

4. **✅ HTTP Verification**: Validate image URLs are accessible
   ```python
   import requests
   http_response = requests.head(image_url, timeout=10)
   assert http_response.status_code == 200, "Image not accessible"
   ```

5. **✅ Persistent URLs**: Image URLs are permanent and hosted on Google Cloud Storage
   - URLs do NOT expire and can be safely stored in databases
   - Format: `https://storage.googleapis.com/fenado-ai-farm-public/generated/{uuid}.webp`
   - Each image gets a unique UUID identifier
   - Safe for long-term storage and embedding in applications

6. **Image Storage**: You can use URLs directly or download for local storage:
   ```python
   import requests
   from pathlib import Path
   import re
   
   async def download_image(response, output_path):
       if response.success:
           urls = re.findall(r'https?://[^\s\)]+', response.content)
           if urls:
               img_response = requests.get(urls[0])
               Path(output_path).write_bytes(img_response.content)
               print(f"Image saved to {output_path}")
   ```

## Troubleshooting

### Tools Not Being Used (`tools_used: False`)
```
❌ CRITICAL FAILURE: MCP tools were NOT used!
❌ The LLM is fabricating image URLs instead of calling MCP!
```
**Solution**:
1. Verify MCP client initialized: `await client.__aenter__()`
2. Check tools loaded: `len(await client.get_tools()) > 0`
3. Ensure transport is correct: Use `"streamable_http"` not `"http"`
4. Verify LangGraph agent created: `create_react_agent(llm, tools)`
5. Check system prompt instructs tool usage

### No MCP Tools Loaded (`tools_available: 0`)
```
❌ No tools available
```
**Solution**: 
- Check `CODEXHUB_MCP_AUTH_TOKEN` is set in `.env` file
- Verify server config uses dict format: `{"server-name": {...}}`
- Ensure `"transport": "streamable_http"` is set
- Call async setup: `await agent.setup_image_mcp()`

### Connection Errors
**Solution**: Verify internet connectivity and that the MCP service is accessible

### HTTP Verification Fails
```
❌ Image URL returned HTTP 403/404
```
**Solution**: 
- LLM may have fabricated the URL - check `tools_used` metadata
- Verify the URL format: `https://storage.googleapis.com/fenado-ai-farm-public/...`
- If the image was just generated, wait a few seconds for upload
- Google Cloud Storage URLs should NOT expire

## Extending the ImageAgent

You can extend the ImageAgent for specific use cases:

```python
class ProductImageAgent(ImageAgent):
    """Specialized agent for generating product images"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        # Override system prompt for product-specific generation
        self.system_prompt = "Generate professional product images..."
    
    async def generate_product_image(self, product_name: str, style: str):
        prompt = f"Generate a professional product image of {product_name} in {style} style"
        return await self.execute(prompt, use_tools=True)
```

## Related Documentation

- [AI Agent Architecture](./aiagent.md)
- [Tech Stack](./techstack.md)
- [Testing Guide](../HOW_TO_TEST.md)

## API Reference

### ImageAgent

#### Methods

- `__init__(config: AgentConfig)`: Initialize the image agent
- `execute(prompt: str, use_tools: bool = True) -> AgentResponse`: Generate images from prompt
- `setup_image_mcp()`: Configure the image generation MCP connection
- `get_capabilities() -> List[str]`: Get agent capabilities

#### Response Format

```python
class AgentResponse:
    success: bool           # Whether generation succeeded
    content: str            # Markdown with image options and URLs
    metadata: Dict[str, Any]  # Model info, tools used, etc.
    error: Optional[str]    # Error message if success=False
```

## License

Part of the FenadoV2 Template project.
