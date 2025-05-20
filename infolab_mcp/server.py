"""MCP server for Infolab integration."""
import asyncio
import logging
from typing import Dict, Any

from dotenv import load_dotenv
from fastmcp import FastMCP, Context
from fastmcp.server.dependencies import get_http_request

from .config.settings import settings
from .infolab.auth import auth_client
from .utils.logging import configure_logging

# Configure logging
configure_logging(log_level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(
    "InfoLabMCPServer",
    dependencies=[
        "httpx",
        "mcp[cli]",
        "pydantic",
        "pydantic-settings",
        "python-dotenv"
    ]
)


async def authenticate() -> bool:
    """
    Authenticate the request and get user info.
    
    Returns:
        A dictionary with user information
        
    Raises:
        ValueError: If authentication fails
    """
    logger.info("Authenticating MCP request")

    try:
        # Get authorization header from context if available
        auth_header = None
        request = get_http_request()
        if request and request.headers:
            # In fastmcp, the context.request.headers is a dictionary-like object
            auth_header = request.headers.get("Authorization")
            logger.debug(f"Found headers in context: {list(request.headers.keys())}")

        # If no header provided by the client, use our cached token
        if not auth_header:
            logger.info("No auth header provided, using cached token")
            valid = await auth_client.validate_token()

            if valid:
                logger.info(f"Using cached token")
                return valid
            else:
                logger.info("Cached token invalid, refreshing")
                # Get a new token and validate it
                token = await auth_client.refresh_token()
                valid = await auth_client.validate_token(token)

                if not valid:
                    raise ValueError("Failed to authenticate with API key")
                return valid
        else:
            # Client provided its own token, validate it
            logger.info("Using client-provided auth header")
            token = auth_header.replace("Bearer ", "")
            valid = await auth_client.validate_token(token)

            if not valid:
                raise ValueError("Invalid client-provided token")
            return valid
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise ValueError(f"Authentication failed: {str(e)}")


@mcp.tool()
async def retrieve_information(message: str, ctx: Context) -> str:
    """
    A dummy tool that demonstrates the authentication flow.

    Args:
        message: A message to echo back
        ctx: The MCP context for the current request

    Returns:
        A string message with user information
    """
    # Log request information from the context
    request = get_http_request()
    if request:
        logger.info(f"Request ID: {ctx.request_id}")
        logger.info(f"Client ID: {ctx.client_id}")
        logger.info(f"Transport Type: {ctx.transport_type if hasattr(ctx, 'transport_type') else 'Unknown'}")

    # Send progress info to the client
    await ctx.info("Processing your request...")

    # Authenticate the request
    try:
        # Report progress
        await ctx.report_progress(0, 2)

        valid = await authenticate()

        # Report progress
        await ctx.report_progress(1, 2)

        # Return a message with the user info
        # todo here
        response = ''

        # Final progress update
        await ctx.report_progress(2, 2)

        return response
    except ValueError as e:
        await ctx.error(f"Authentication error: {str(e)}")
        return f"Authentication error: {str(e)}"
    except Exception as e:
        logger.error(f"Error in dummy_tool: {str(e)}")
        await ctx.error(f"An unexpected error occurred: {str(e)}")
        return f"Error: {str(e)}"


async def shutdown():
    """Clean up resources on shutdown."""
    logger.info("Shutting down Infolab MCP server")
    if auth_client:
        await auth_client.close()


async def startup():
    """Initialize services on startup."""
    logger.info("Starting Infolab MCP server")

    # Test authentication flow
    try:
        token = await auth_client.get_token()
        valid = await auth_client.validate_token(token)
        if valid:
            logger.info(f"Authentication test successful")
        else:
            logger.warning("Authentication test failed - token invalid")
    except Exception as e:
        logger.error(f"Authentication test failed: {str(e)}")


def main():
    """Main function for running the Infolab server."""
    load_dotenv()
    logger.info("Starting Infolab MCP server...")

    # Create event loop to run startup tasks
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Run startup tasks
        loop.run_until_complete(startup())

        # Run the MCP server with SSE transport
        logger.info("Starting MCP server with SSE transport on port 8000")
        mcp.run(transport="sse", host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Error running MCP server: {str(e)}")
    finally:
        try:
            # Ensure shutdown tasks run
            if not loop.is_closed():
                loop.run_until_complete(shutdown())
                loop.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")


if __name__ == "__main__":
    main()
