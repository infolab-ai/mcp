"""MCP server for Infolab integration."""
import asyncio
import logging

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request

from .config.settings import settings
from .infolab.auth import auth_client
from .infolab.client import api_client
from .utils.logging import configure_logging
from .tools.user_options import get_user_options
from .tools.marketplace import search_marketplace
from .tools.information import retrieve_information
from .tools.contribution import contribute
from .tools.persona import get_persona, refresh_persona

# Configure logging
configure_logging(log_level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(
    "InfoLabMCPServer",
    instructions="""
    Welcome to the InfoLab MCP Server!
    
    This server provides tools to interact with the InfoLab platform:
    
    1. `get_user_options` - Get information about your available courses, modules, and files.
    2. `search_marketplace` - Search for courses in the marketplace.
    3. `retrieve_information` - Get information from course content.
    4. `contribute` - Add content to a course.
    5. `get_persona` - Get information about a persona.
    6. `refresh_persona` - Update a persona's content.
    
    Start by calling `get_user_options` to see what courses and modules you have access to.
    """,
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


# Register tools
mcp.tool()(get_user_options)
mcp.tool()(search_marketplace)
mcp.tool()(retrieve_information)
mcp.tool()(contribute)
mcp.tool()(get_persona)
mcp.tool()(refresh_persona)


async def shutdown():
    """Clean up resources on shutdown."""
    logger.info("Shutting down Infolab MCP server")
    if auth_client:
        await auth_client.close()
    if api_client:
        await api_client.close()


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
        logger.info("Starting MCP server with Streamable HTTP transport on port 8080 at path /mcp")
        mcp.run(transport="streamable-http", host="::", port=8080, path="/mcp")
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
