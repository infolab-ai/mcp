"""User options MCP tool."""
import asyncio
import logging
from typing import Dict, Any

from fastmcp import Context

from ..huuh.client import api_client
from ..utils.auth_wrapper import ensure_authenticated_async, get_error_response

logger = logging.getLogger(__name__)


async def get_user_options(ctx: Context) -> Dict[str, Any]:
    """
    Retrieve user options and preferences for the authenticated user.
    
    This tool provides information about the user's available courses,
    modules, groups, and files that can be used with other tools.
    
    Returns:
        A dictionary containing user options and settings.
    """
    try:
        # Report start
        await ctx.info("Retrieving user options...")
        await ctx.report_progress(0, 2)
        
        # Authenticate
        await ctx.info("Authenticating...")
        if not await ensure_authenticated_async():
            await ctx.error("Authentication failed")
            return get_error_response("Please check your credentials.")
        
        # Request user options
        await ctx.report_progress(1, 2)
        await ctx.info("Fetching user options...")
        
        try:
            response = await api_client.request("GET", "/mcp/user_options")
            
            # Report completion
            await ctx.report_progress(2, 2)
            await ctx.info("User options retrieved successfully")
            
            return response
        except ValueError as e:
            await ctx.error(f"Error fetching user options: {str(e)}")
            return {"error": f"Error fetching user options: {str(e)}"}
    except Exception as e:
        logger.exception("Unexpected error in get_user_options")
        await ctx.error("An unexpected error occurred")
        return {"error": f"An unexpected error occurred: {str(e)}"}
