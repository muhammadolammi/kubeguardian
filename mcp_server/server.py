import os


import asyncio
import json
from dotenv import load_dotenv
import logging
# MCP Imports
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# ADK Tool Imports
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type
from tools.custom_tools import get_devs_name , filesystem # Your callable 
from const import logger



# --- Load environment variables ---
load_dotenv()
def get_chat_mode() -> bool:
    try:
        with open("chat.env", "r") as f:
            for line in f:
                if line.startswith("CHAT_MODE"):
                    # Extract value after '=' and convert to bool
                    value = line.split("=", 1)[1].strip()
                    return value.lower() == "true"
    except FileNotFoundError:
        return False  # Default if file missing

    return False  # Default fallback

chat_mode = get_chat_mode()
logging.disable(logging.CRITICAL if chat_mode else logging.NOTSET)


# --- Prepare ADK Tools ---
logger.info("Initializing ADK tools...")
#TODO theres an option to change the allowed files_directory here , default is cwd/app
f = filesystem()


tools = {
    "get_devs_name": FunctionTool(get_devs_name),
    "get_files_info": FunctionTool(f.get_files_info),
    "get_file_content": FunctionTool(f.get_file_content),
    "get_absolute_path": FunctionTool(f.get_absolute_path),
    }
logger.info(f"ADK tools {list(tools.keys())} initialized and ready to be exposed via MCP.")

# --- MCP Server Setup ---
logger.info("Creating MCP Server instance...")
app = Server("adk-tools-exposing-mcp-server")

@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """MCP handler to list tools this server exposes."""
    logger.info("MCP Server: Received list_tools request.")
    schemas = [adk_to_mcp_tool_type(tool) for tool in tools.values()]
    logger.info(f"MCP Server: Advertising tools: {[schema.name for schema in schemas]}")
    return schemas


@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    """MCP handler to execute a tool call requested by an MCP client."""
    logger.info(f"MCP Server: Received call_tool request for '{name}' with args: {arguments}")
    if name in tools:
        try:
            adk_tool_response = await tools[name].run_async(args=arguments, tool_context=None)
            logger.info(f"MCP Server: ADK tool '{name}' executed successfully.")
            return [mcp_types.TextContent(type="text", text=json.dumps(adk_tool_response, indent=2))]
        except Exception as e:
            logger.exception(f"Error executing ADK tool '{name}': {e}")
            return [mcp_types.TextContent(type="text", text=json.dumps({"error": str(e)}))]
    else:
        logger.warning(f"Tool '{name}' not found.")
        return [mcp_types.TextContent(type="text", text=json.dumps({"error": f"Tool '{name}' not implemented"}))]


# --- MCP Server Runner ---
async def run_mcp_stdio_server():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("MCP Stdio Server: Starting handshake with client...")
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
        logger.info("MCP Stdio Server: Run loop finished or client disconnected.")


if __name__ == "__main__":
    logger.info("Launching MCP Server to expose ADK tools via stdio...")
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        logger.info("MCP Server (stdio) stopped by user.")
    except Exception as e:
        logger.exception(f"MCP Server (stdio) encountered an error: {e}")
    finally:
        logger.info("MCP Server (stdio) process exiting.")
