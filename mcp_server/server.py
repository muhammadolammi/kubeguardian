from const import logger 

import contextlib
import logging
from collections.abc import AsyncIterator
from typing import Any
import json
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type
from custom_tools import get_devs_name, get_all_manifests, get_absolute_path, get_manifest, create_alert

# -----------------------[ADK Tools Setup]-----------------------
tools = {
    "get_devs_name": FunctionTool(get_devs_name),
    "get_manifest": FunctionTool(get_manifest),
    "get_all_manifests": FunctionTool(get_all_manifests),
    "get_absolute_path": FunctionTool(get_absolute_path),
    "create_alert": FunctionTool(create_alert),
}

logger.info(f"ADK tools {list(tools.keys())} initialized.")

# -----------------------[Create MCP Server]-----------------------
def create_mcp_server() -> Server:
    app = Server("adk-tools-mcp-streamable-server")

    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
        logger.info(f"Tool called: {name} with arguments: {arguments}")
        if name not in tools:
            return [
                types.TextContent(
                    type="text",
                    text=f"Tool '{name}' not implemented"
                )
            ]

        try:
            # Run ADK tool asynchronously
            result = await tools[name].run_async(args=arguments, tool_context=None)
            return [
                types.TextContent(
                    type="text",
                    text=f"{json.dumps(result, indent=2)}"
                )
            ]
        except Exception as e:
            logger.exception(f"Error executing tool '{name}': {e}")
            return [
                types.TextContent(
                    type="text",
                    text=f"Error executing tool '{name}': {str(e)}"
                )
            ]

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [adk_to_mcp_tool_type(tool) for tool in tools.values()]

    return app

# -----------------------[Run Streamable HTTP MCP Server]-----------------------
def main(json_response: bool = False):
    logging.basicConfig(level=logging.INFO)
    app = create_mcp_server()

    # Streamable session manager (stateless for Cloud Run)
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=json_response,
        stateless=True
    )

    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send):
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        async with session_manager.run():
            logger.info("MCP Streamable HTTP server started!")
            try:
                yield
            finally:
                logger.info("MCP server shutting down...")

    # ASGI application
    starlette_app = Starlette(
        debug=False,
        routes=[Mount("/mcp", app=handle_streamable_http)],
        lifespan=lifespan
    )

    import uvicorn
    uvicorn.run(starlette_app, host="0.0.0.0", port=8086)

if __name__ == "__main__":
    main()
