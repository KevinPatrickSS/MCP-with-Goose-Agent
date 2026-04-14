"""
MCP Server for Resort Booking System
Exposes tools to Goose AI agent via Model Context Protocol
"""
import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import your existing tools and schemas
from tools import call_tool
from schemas import ALL_FUNCTION_SCHEMAS

# Create MCP server instance
app = Server("resort-booking-server")

@app.list_tools()
async def list_tools():
    tools = []
    
    for schema in ALL_FUNCTION_SCHEMAS:
        func_info = schema["function"]

        tool = Tool(
            name=func_info["name"],
            description=func_info["description"],
            inputSchema=func_info["parameters"]
        )
        tools.append(tool)

    # MUST return dict, not list
    return {"tools": tools}

@app.call_tool()
async def call_tool_handler(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Handle tool execution requests from Goose.
    
    Args:
        name: Tool name to execute
        arguments: Tool arguments as dictionary
        
    Returns:
        List of TextContent with tool results
    """
    try:
        # Call your existing tool function
        result = call_tool(name, **arguments)
        
        # Format result as JSON string
        if isinstance(result, dict):
            result_str = json.dumps(result, indent=2, default=str)
        else:
            result_str = json.dumps({"result": result}, indent=2, default=str)
        
        # Return in MCP format
        return [
            TextContent(
                type="text",
                text=result_str
            )
        ]
    
    except Exception as e:
        # Return error in MCP format
        error_msg = json.dumps({
            "error": str(e),
            "tool": name,
            "arguments": arguments
        }, indent=2)
        
        return [
            TextContent(
                type="text",
                text=error_msg
            )
        ]

async def main():
    """Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())