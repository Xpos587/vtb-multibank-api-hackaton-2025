#!/usr/bin/env python3
"""
MCP Perplexity Research Server using OpenAI SDK
Simplified version with automatic model selection
"""
import asyncio
import os
import logging
from pathlib import Path
from typing import Dict, List

from fastmcp import FastMCP
from openai import AsyncOpenAI

# Configure logging
LOG_PATH = Path(__file__).parent.parent / "logs" / "pplx-research.log"
LOG_PATH.parent.mkdir(exist_ok=True)

logger = logging.getLogger("pplx_research_mcp")
logger.setLevel(logging.ERROR)

# Create file handler
LOGS_FILE_PATH = Path(__file__).parent.parent / "logs" / "pplx-research.log"
LOGS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
file_handler = logging.FileHandler(LOGS_FILE_PATH, mode="a")
file_handler.setLevel(logging.ERROR)

# Create formatter and add to handler
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s - %(message)s - %(filename)s:%(lineno)d"
)
file_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(file_handler)
logger.info(f"Logging initialized to {LOGS_FILE_PATH}")

# Global OpenAI client
client = None


def handle_error(error: Exception) -> str:
    """Simple error handling function."""
    error_msg = str(error)

    if "401" in error_msg or "unauthorized" in error_msg.lower():
        return "❌ Invalid API key. Please check your PERPLEXITY_API_KEY."
    elif "429" in error_msg or "quota" in error_msg.lower():
        return "❌ Rate limit exceeded. Please wait a moment before retrying."
    elif "timeout" in error_msg.lower():
        return "❌ Request timed out. Try using 'quick' reasoning effort."
    else:
        logger.exception(f"Research failed: {error}")
        return f"❌ Research failed: {error_msg}"


# Model configurations based on reasoning effort
def get_optimal_config(reasoning_effort: str) -> dict:
    """Get optimal model configuration based on reasoning effort level."""
    configs = {
        "quick": {
            "model": "sonar",
            "timeout": 30,
            "max_tokens": 500,
            "temperature": 0.3,
        },
        "low": {
            "model": "sonar-reasoning-pro",
            "timeout": 60,
            "max_tokens": 1000,
            "temperature": 0.3,
        },
        "medium": {
            "model": "sonar-reasoning-pro",
            "timeout": 120,
            "max_tokens": 2000,
            "temperature": 0.5,
        },
        "high": {
            "model": "sonar-deep-research",
            "timeout": 600,
            "max_tokens": 4000,
            "temperature": 0.7,
        },
    }

    if reasoning_effort not in configs:
        raise ValueError(f"Invalid reasoning_effort: {reasoning_effort}")

    return configs[reasoning_effort]


async def init_openai_client() -> AsyncOpenAI:
    """Initialize Async OpenAI client with Perplexity configuration."""
    global client

    if client:
        return client

    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY environment variable is required")

    client = AsyncOpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
    return client


def format_research_result(
    content: str,
    citations: List[Dict],
) -> str:
    """Format research results with user-friendly information."""
    # Add citations if available
    if citations:
        content += "\n\nCitations:\n"
        for i, citation in enumerate(citations[:10], 1):
            title = citation["title"]
            url = citation["url"]
            date = citation["date"]

            content += f"{i}. [{title}]({url})"
            if date:
                content += f" ({date})"
            content += "\n\n"
    return content


# Initialize MCP
mcp = FastMCP("pplx-research")


@mcp.tool()
async def research(query: str, reasoning_effort: str) -> str:
    """
    Perform intelligent research with automatic model selection using OpenAI SDK.

    Args:
        query: The research question or topic
        reasoning_effort: Research depth level:
            - "quick": Fast basic facts (30s, sonar model)
            - "low": Quick reasoning (1min, sonar-reasoning-pro)
            - "medium": Balanced analysis (2min, sonar-reasoning-pro)
            - "high": Deep comprehensive research (10min, sonar-deep-research)

    Returns:
        Formatted research results with citations

    Prompting Best Practices:
        • BE SPECIFIC: Add 2-3 extra words of context for better search results
        • AVOID FEW-SHOT: Don't use examples in prompts - they confuse web search
        • THINK LIKE SEARCH: Use terms that would appear on relevant web pages
        • ONE TOPIC: Focus on single subject per query for best results
        • NO URLs: Never ask for links in prompts - use API search_results instead
        • ACCESSIBLE SOURCES: Request info from publicly available sources only

    Examples:
        ✅ Good: "Compare energy efficiency ratings of heat pumps vs traditional HVAC for residential use"
        ❌ Bad: "Tell me about heating systems"
    """
    try:
        # Validate input
        if not query or len(query) > 8000:
            return "❌ Query must be 1-8000 characters"

        valid_efforts = ["quick", "low", "medium", "high"]
        if reasoning_effort not in valid_efforts:
            return f"❌ reasoning_effort must be one of: {', '.join(valid_efforts)}"

        # Get optimal configuration automatically
        config = get_optimal_config(reasoning_effort)

        # Initialize OpenAI client
        openai_client = await init_openai_client()

        # Prepare messages
        messages = [{"role": "user", "content": query}]

        # Build request parameters
        request_params = {
            "model": config["model"],
            "messages": messages,
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"],
        }

        # Add Perplexity-specific parameters for deep research
        if config["model"] == "sonar-deep-research":
            # Map reasoning_effort to deep research parameters
            effort_mapping = {
                "quick": "low",
                "low": "low",
                "medium": "medium",
                "high": "high",
            }
            request_params["extra_body"] = {
                "reasoning_effort": effort_mapping.get(reasoning_effort, "medium")
            }

        # Make the request using OpenAI SDK with custom timeout
        try:
            response = await asyncio.wait_for(
                openai_client.chat.completions.create(**request_params),
                timeout=config["timeout"],
            )
        except asyncio.TimeoutError:
            return f"❌ Request timed out after {config['timeout']} seconds. Try using 'quick' reasoning effort."

        # Extract the research results
        content = response.choices[0].message.content
        citations = []

        # Extract citations from response metadata if available
        if hasattr(response, "search_results") and response.search_results:
            citations = response.search_results

        # Format and return results
        formatted_result = format_research_result(
            content=content,
            citations=citations,
        )

        return formatted_result

    except Exception as e:
        return handle_error(e)


async def main():
    """Run MCP server."""
    # Initialize OpenAI client at startup
    try:
        await init_openai_client()
        print("Perplexity Research MCP Server (OpenAI SDK) initialized successfully")
    except Exception as e:
        print(f"Startup failed: {e}")
        return

    try:
        await mcp.run_stdio_async()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Server error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
