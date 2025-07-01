"""Space management MCP tools."""
import logging
from typing import Dict, Any

from fastmcp import Context

from ..huuh.client import api_client
from ..utils.auth_wrapper import ensure_authenticated_async, get_error_response

logger = logging.getLogger(__name__)


async def create_spaces(
        space_name: str,
        space_description: str,
        ctx: Context = None
) -> Dict[str, Any]:
    """
    Create a new space.

    Args:
        space_name: Name of the space
        space_description: Description of the space

    Returns:
        A dictionary containing the result of the space creation.
    """
    logger.info(f"create_spaces called with space_name='{space_name}'")

    try:
        await ctx.info(f"Creating space '{space_name}'...")
        await ctx.report_progress(0, 3)

        # Authenticate
        await ctx.info("Authenticating...")
        if not await ensure_authenticated_async():
            await ctx.error("Authentication failed")
            return get_error_response("Please check your credentials.")

        # Validate inputs
        if not space_name or not space_description:
            await ctx.error(
                "Missing required parameters: space_name and space_description must be provided.")
            return {
                "error": "Missing required parameters: space_name and space_description must be provided."}

        await ctx.report_progress(1, 3)

        try:
            data = {
                "space_name": space_name,
                "space_description": space_description
            }
            headers = {"Content-Type": "application/json"}
            response = await api_client.request(
                method="POST",
                endpoint="/mcp/create_spaces",
                json=data,
                headers=headers
            )

            await ctx.report_progress(3, 3)
            await ctx.info("Space created successfully")

            return response
        except ValueError as e:
            await ctx.error(f"Error creating space: {str(e)}")
            return {"error": f"Error creating space: {str(e)}"}
    except Exception as e:
        logger.exception("Unexpected error in create_spaces")
        await ctx.error("An unexpected error occurred")
        return {"error": f"An unexpected error occurred: {str(e)}"}
