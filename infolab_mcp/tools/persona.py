"""Persona management MCP tools."""
import logging
from typing import Dict, Any, Optional
from urllib.parse import quote

from fastmcp import Context

from ..infolab.auth import auth_client
from ..infolab.client import api_client

logger = logging.getLogger(__name__)


async def get_persona(title: str, ctx: Context) -> Dict[str, Any]:
    """
    Get persona information by title.
    
    Args:
        title: Title of the persona
        
    Returns:
        A dictionary containing persona information.
    """
    try:
        # Report start
        await ctx.info(f"Retrieving persona '{title}'...")
        await ctx.report_progress(0, 2)
        
        # Authenticate
        valid = await auth_client.validate_token()
        if not valid:
            await ctx.error("Authentication failed")
            return {"error": "Authentication failed. Please check your credentials."}
        
        # Request persona
        await ctx.report_progress(1, 2)
        await ctx.info("Fetching persona information...")
        
        try:
            response = await api_client.request(
                "GET", 
                f"/mcp/get_persona?title={quote(title)}"
            )
            
            # Report completion
            await ctx.report_progress(2, 2)
            await ctx.info("Persona retrieved successfully")
            
            return response
        except ValueError as e:
            await ctx.error(f"Error retrieving persona: {str(e)}")
            return {"error": f"Error retrieving persona: {str(e)}"}
    except Exception as e:
        logger.exception("Unexpected error in get_persona")
        await ctx.error("An unexpected error occurred")
        return {"error": f"An unexpected error occurred: {str(e)}"}


async def refresh_persona(
    title: str,
    new_content: str,
    course_id: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Update persona content.
    
    Args:
        title: Title of the persona to update
        new_content: New content for the persona
        course_id: Optional ID of the course if it's a course persona
        
    Returns:
        A dictionary containing the result of the update.
    """
    try:
        # Report start
        await ctx.info(f"Updating persona '{title}'...")
        await ctx.report_progress(0, 2)
        
        # Authenticate
        valid = await auth_client.validate_token()
        if not valid:
            await ctx.error("Authentication failed")
            return {"error": "Authentication failed. Please check your credentials."}
        
        # Update persona
        await ctx.report_progress(1, 2)
        await ctx.info("Updating persona content...")
        
        try:
            # Prepare data
            data = {
                "title": title,
                "new_content": new_content
            }
            if course_id:
                data["course_id"] = course_id
            
            # Make request
            response = await api_client.request("POST", "/mcp/refresh_persona", json=data)
            
            # Report completion
            await ctx.report_progress(2, 2)
            await ctx.info("Persona updated successfully")
            
            return response
        except ValueError as e:
            await ctx.error(f"Error updating persona: {str(e)}")
            return {"error": f"Error updating persona: {str(e)}"}
    except Exception as e:
        logger.exception("Unexpected error in refresh_persona")
        await ctx.error("An unexpected error occurred")
        return {"error": f"An unexpected error occurred: {str(e)}"}
