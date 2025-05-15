"""MCP server for Infolab integration."""
import logging
import webbrowser
from typing import List

from dotenv import load_dotenv
from fastmcp import FastMCP, Context
from pydantic import FilePath

from .callback_server import InfolabCallbackServer
from .utils.logging import configure_logging
from .config.settings import settings

# Configure logging
configure_logging(
    log_level=settings.LOG_LEVEL,
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(
    "InfolabServer",
    dependencies=[
        "httpx",
        "mcp[cli]",
        "pydantic",
        "pydantic-settings",
        "python-dotenv"
    ]
)

# Initialize clients


@mcp.tool()
async def retrieve_information(ctx: Context = None) -> str:
    """Retrieve information from Infolab."""
    # todo to be implemented
    pass

@mcp.tool()
async def contribute_information(ctx: Context = None) -> str:
    """Contribute information to Infolab."""
    # todo to be implemented
    pass


def main():
    """Main function for running the Infolab server."""
    load_dotenv()
    logger.info("Starting Infolab server...")
    mcp.run()


if __name__ == "__main__":
    main()
