"""Synchronous authentication wrapper for tools."""
import asyncio
import logging
from typing import Any, Dict

from ..huuh.auth import auth_client

logger = logging.getLogger(__name__)


def ensure_authenticated() -> bool:
    """
    Ensure authentication is valid before tool execution.
    
    This function runs the authentication check synchronously by creating
    an event loop if needed.
    
    Returns:
        bool: True if authentication is successful, False otherwise
    """
    try:
        # Try to get current event loop
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, we need to run in a thread
            # But since we're being called from async functions anyway,
            # let's create a task and run it
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run_auth_in_new_loop)
                return future.result(timeout=30)  # 30 second timeout
        except RuntimeError:
            # No running loop, we can create our own
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(_authenticate())
            finally:
                loop.close()
                
    except Exception as e:
        logger.error(f"Authentication wrapper error: {str(e)}")
        return False


def _run_auth_in_new_loop() -> bool:
    """
    Run authentication in a new event loop (for thread execution).
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_authenticate())
    finally:
        loop.close()


async def ensure_authenticated_async() -> bool:
    """
    Async version of ensure_authenticated for use in async contexts.
    
    Returns:
        bool: True if authentication is successful, False otherwise
    """
    return await _authenticate()


async def _authenticate() -> bool:
    """
    Internal async authentication function.
    
    Returns:
        bool: True if authentication is successful, False otherwise
    """
    try:
        logger.info("Authenticating MCP request")
        
        # Try to get and validate current token
        valid = await auth_client.validate_token()
        
        if valid:
            logger.info("Using cached token")
            return True
        else:
            logger.info("Cached token invalid, refreshing")
            # Get a new token and validate it
            token = await auth_client.refresh_token()
            valid = await auth_client.validate_token(token)
            
            if not valid:
                logger.error("Failed to authenticate with API key")
                return False
            return True
            
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return False


def get_error_response(message: str) -> Dict[str, Any]:
    """
    Create a standard error response for authentication failures.
    
    Args:
        message: Error message to include
        
    Returns:
        Dict containing error response
    """
    return {"error": f"Authentication failed: {message}"}
