# Test extensible AI agents library

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load env from backend
load_dotenv(backend_dir / ".env")

async def test_search_agent():
    # Test AI agents with web search
    print("🧪 Search Agent Test")
    print("=" * 30)
    
    # Set model name
    os.environ['AI_MODEL_NAME'] = 'gemini-2.5-pro'
    
    try:
        from ai_agents import SearchAgent, AgentConfig
        
        config = AgentConfig()
        print(f"LiteLLM Token: {config.api_key[:10]}...")
        print(f"Model: {config.model_name}")
        print(f"LiteLLM Base URL: {config.api_base_url}")
        
        search_agent = SearchAgent(config)
        
        print("\n🌍 Question: What is today's weather in Tokyo?")
        print("Searching web...")
        
        response = await search_agent.execute(
            "Use web search to find today's current weather in Tokyo, Japan", 
            use_tools=True
        )
        
        print(f"\n✅ Success: {response.success}")
        print(f"ℹ️  Metadata: {response.metadata}")
        print(f"ℹ️  MCP Tools Available: {len(search_agent.mcp_tools)}")
        print(f"ℹ️  MCP Tools Actually Used: {response.metadata.get('tools_used', False)}")
        
        if response.success:
            print(f"\n📝 Full Response:\n{response.content[:300]}...\n")
            
            # CRITICAL: Check if MCP tools were actually used
            tools_used = response.metadata.get('tools_used', False)
            if not tools_used:
                print("\n❌ CRITICAL FAILURE: MCP tools were NOT used!")
                print("❌ The LLM is answering without web search!")
                print(f"❌ Tools available: {len(search_agent.mcp_tools)}")
                return False
            
            # Check for weather-related keywords
            weather_keywords = ['weather', 'temperature', 'tokyo', 'celsius', 'fahrenheit', 'sunny', 'cloudy', 'rain']
            content_lower = response.content.lower()
            if any(keyword in content_lower for keyword in weather_keywords):
                print("🎯 CORRECT: MCP tools were used and weather information found!")
                return True
            else:
                print("⚠️  Response doesn't contain expected weather information")
                return False
        else:
            print(f"❌ Error: {response.error}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_image_agent():
    # Test AI agents with image generation
    print("\n🧪 Image Agent Test")
    print("=" * 30)
    
    # Set model name
    os.environ['AI_MODEL_NAME'] = 'gemini-2.5-pro'
    
    try:
        from ai_agents import ImageAgent, AgentConfig
        
        config = AgentConfig()
        print(f"LiteLLM Token: {config.api_key[:10]}...")
        print(f"Model: {config.model_name}")
        print(f"LiteLLM Base URL: {config.api_base_url}")
        
        image_agent = ImageAgent(config)
        
        print("\n🎨 Prompt: Generate an image of a sunset over mountains")
        print("Generating image...")
        
        response = await image_agent.execute(
            "Generate an image of a sunset over mountains", 
            use_tools=True
        )
        
        print(f"\n✅ Success: {response.success}")
        print(f"ℹ️  Metadata: {response.metadata}")
        print(f"ℹ️  MCP Tools Available: {len(image_agent.mcp_tools)}")
        print(f"ℹ️  MCP Tools Actually Used: {response.metadata.get('tools_used', False)}")
        
        if response.success:
            print(f"\n📝 Full Response:\n{response.content}\n")
            
            # Extract and display image URLs
            import re
            urls = re.findall(r'https?://[^\s\)]+', response.content)
            if urls:
                print("🖼️  Image URLs found:")
                for i, url in enumerate(urls, 1):
                    print(f"   {i}. {url}")
                    # Validate it's a real Google Cloud Storage URL
                    if 'storage.googleapis.com' in url:
                        print(f"      ✅ Valid Google Cloud Storage URL")
                    else:
                        print(f"      ⚠️  Warning: Not a Google Cloud Storage URL - might be fabricated!")
            
            # CRITICAL: Check if MCP tools were actually used
            tools_used = response.metadata.get('tools_used', False)
            if not tools_used:
                print("\n❌ CRITICAL FAILURE: MCP tools were NOT used!")
                print("❌ The LLM is fabricating image URLs instead of calling MCP!")
                print(f"❌ Tools available: {len(image_agent.mcp_tools)}")
                return False
            
            # Check if response contains real image URLs
            if urls and 'storage.googleapis.com' in urls[0]:
                # HTTP verification: Check if image URL is actually accessible
                print("\n🔍 Verifying image URL accessibility...")
                import requests
                try:
                    http_response = requests.head(urls[0], timeout=10)
                    print(f"   HTTP Status: {http_response.status_code}")
                    
                    if http_response.status_code == 200:
                        print("   ✅ Image URL is accessible (HTTP 200)")
                        print("\n🎯 CORRECT: MCP tools were used and real image generated!")
                        print(f"   ✅ Image URL verified: {urls[0]}")
                        return True
                    else:
                        print(f"   ❌ Image URL returned HTTP {http_response.status_code}")
                        print("   ⚠️  URL may not be accessible")
                        return False
                except requests.RequestException as e:
                    print(f"   ❌ Failed to verify URL: {e}")
                    return False
            else:
                print("\n⚠️  Warning: Response doesn't contain valid Google Cloud Storage URLs")
                return False
        else:
            print(f"❌ Error: {response.error}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_image_agent_structured():
    # Test AI agents with structured JSON output
    print("\n🧪 Image Agent Structured Output Test")
    print("=" * 30)
    
    # Set model name
    os.environ['AI_MODEL_NAME'] = 'gemini-2.5-pro'
    
    try:
        from ai_agents import ImageAgent, AgentConfig, ImageGenerationResult
        
        config = AgentConfig()
        image_agent = ImageAgent(config)
        
        print("\n🎨 Prompt: Generate an image of a futuristic city")
        print("Generating image with structured output...")
        
        result: ImageGenerationResult = await image_agent.generate_image_structured(
            "Generate an image of a futuristic city with flying cars"
        )
        
        print(f"\n✅ Success: {result.success}")
        print(f"📝 Image URL: {result.image_url}")
        print(f"📝 Description: {result.description}")
        print(f"📝 Source: {result.source}")
        
        # Validate structured output
        if result.success:
            if result.image_url and 'storage.googleapis.com' in result.image_url:
                # HTTP verification: Check if image URL is actually accessible
                print("\n🔍 Verifying image URL accessibility...")
                import requests
                try:
                    http_response = requests.head(result.image_url, timeout=10)
                    print(f"   HTTP Status: {http_response.status_code}")
                    
                    if http_response.status_code == 200:
                        print("   ✅ Image URL is accessible (HTTP 200)")
                        print("\n🎯 CORRECT: Structured output with verified image URL!")
                        print(f"   ✅ Image URL: {result.image_url}")
                        print(f"   📝 Description: {result.description}")
                        print(f"   📝 Source: {result.source}")
                        return True
                    else:
                        print(f"   ❌ Image URL returned HTTP {http_response.status_code}")
                        return False
                except requests.RequestException as e:
                    print(f"   ❌ Failed to verify URL: {e}")
                    return False
            else:
                print("\n❌ FAILURE: Image URL is invalid or fabricated!")
                return False
        else:
            print(f"\n❌ FAILURE: {result.description}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Running AI Agents Tests")
    print("=" * 50)
    
    # Test search agent
    search_success = asyncio.run(test_search_agent())
    
    # Test image agent
    image_success = asyncio.run(test_image_agent())
    
    # Test image agent with structured output
    structured_success = asyncio.run(test_image_agent_structured())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"  Search Agent:           {'✅ PASSED' if search_success else '❌ FAILED'}")
    print(f"  Image Agent:            {'✅ PASSED' if image_success else '❌ FAILED'}")
    print(f"  Structured Output:      {'✅ PASSED' if structured_success else '❌ FAILED'}")
    
    if search_success and image_success and structured_success:
        print("\n🎉 All AI Agents tests passed!")
        print("✅ MCP tools are properly invoked (not fabricated)")
        print("✅ Structured JSON output working correctly")
        print("✅ Images verified from Google Cloud Storage")
        print("💡 You can now extend BaseAgent to create custom AI agents")
    else:
        print("\n⚠️  Some tests failed")
        if not image_success or not structured_success:
            print("⚠️  Image generation tests failed - MCP tools may not be properly loaded")
        print("🔧 Check your CODEXHUB_MCP_AUTH_TOKEN and MCP configuration")
