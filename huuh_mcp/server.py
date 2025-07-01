"""MCP server for huuh integration."""
import argparse
import logging
import socket

from dotenv import load_dotenv
from fastmcp import FastMCP

from .config.settings import settings
from .utils.logging import configure_logging
from .tools.user_options import get_user_options
from .tools.marketplace import search_marketplace
from .tools.information import retrieve_information
from .tools.contribution import contribute
from .tools.persona import get_persona, refresh_persona, contribute_persona_to_course, contribute_persona_to_user
from .tools.base import create_base, assign_base_to_space
from .tools.space import create_spaces


# Configure logging
configure_logging(log_level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(
    "HuuhMCPServer",
    instructions="""
    Welcome to the huuh MCP Server!
    
    This server provides tools to interact with the huuh platform:
    
    1. `get_user_options` - Get information about your available courses, modules, and files.
    2. `search_marketplace` - Search for courses in the marketplace.
    3. `retrieve_information` - Get information from course content.
    4. `contribute` - Add content to a course.
    5. `get_persona` - Get information about a persona.
    6. `refresh_persona` - Update a persona's content.
    7. `contribute_persona_to_course` - Contribute a new persona to a course.
    8. `contribute_persona_to_user` - Contribute a new persona to a user.
    9. `create_base` - Create a new knowledge base for a user.
    10. `assign_base_to_space` - Assign a base to a space.
    11. `create_spaces` - Create a new space.
    
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






# Register tools with explicit parameters

# Register get_user_options with annotations
mcp.tool(
    annotations={
        "name": "get_user_options",
        "description": "Get information about available courses, modules, and files",
        "parameters": {}
    }
)(get_user_options)

# Register search_marketplace with annotations
mcp.tool(
    annotations={
        "name": "search_marketplace",
        "description": "Search for courses in the marketplace",
        "parameters": {
            "query": {
                "type": "string",
                "description": "Search query string (max 150 characters)"
            }
        }
    }
)(search_marketplace)

# Register retrieve_information with annotations
mcp.tool(
    annotations={
        "name": "retrieve_information",
        "description": "Retrieve information from course content",
        "parameters": {
            "query": {
                "type": "string",
                "description": "Search query (max 150 characters)"
            },
            "course_id": {
                "type": "string",
                "description": "ID of the course to search in"
            },
            "relevant_modules": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of module numbers to search in (optional)"
            },
            "relevant_groups": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of group IDs to search in (optional)"
            },
            "relevant_file_ids": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of file IDs to search in (optional)"
            }
        }
    }
)(retrieve_information)

# Register contribute with annotations
mcp.tool(
    annotations={
        "name": "contribute",
        "description": "Add a contribution to a course",
        "parameters": {
            "course_id": {
                "type": "string",
                "description": "ID of the course to contribute to"
            },
            "week_number": {
                "type": "string",
                "description": "Week number to add the contribution to"
            },
            "contribution_title": {
                "type": "string",
                "description": "Title of the contribution"
            },
            "contribution_content": {
                "type": "string",
                "description": "Content of the contribution (max 30,000 characters)"
            }
        }
    }
)(contribute)

# Register get_persona with annotations
mcp.tool(
    annotations={
        "name": "get_persona",
        "description": "Get information about a persona",
        "parameters": {
            "title": {
                "type": "string",
                "description": "Title of the persona to retrieve"
            }
        }
    }
)(get_persona)

# Register refresh_persona with explicit parameter descriptions
mcp.tool(
    annotations={
        "name": "refresh_persona",
        "description": "Update persona content",
        "parameters": {
            "title": {
                "type": "string",
                "description": "Title of the persona to update"
            },
            "new_content": {
                "type": "string",
                "description": "New content for the persona"
            },
            "course_id": {
                "type": "string",
                "description": "ID of the course if it's a course persona (optional)"
            }
        }
    }
)(refresh_persona)

# Register contribute_persona_to_course with explicit parameter descriptions
mcp.tool(
    annotations={
        "name": "contribute_persona_to_course",
        "description": "Contribute a new persona to a course",
        "parameters": {
            "course_id": {
                "type": "string",
                "description": "ID of the course to contribute to"
            },
            "persona_title": {
                "type": "string",
                "description": "Title of the new persona"
            },
            "persona_content": {
                "type": "string",
                "description": "Content of the new persona"
            }
        }
    }
)(contribute_persona_to_course)

mcp.tool(
    annotations={
        "name": "contribute_persona_to_user",
        "description": "Contribute a new persona to the user",
        "parameters": {
            "user_id": {
                "type": "string",
                "description": "ID of the user to contribute to"
            },
            "persona_title": {
                "type": "string",
                "description": "Title of the new persona"
            },
            "persona_content": {
                "type": "string",
                "description": "Content of the new persona"
            }
        }
    }
)(contribute_persona_to_user)

mcp.tool(
    annotations={
        "name": "create_base",
        "description": "Create a base",
        "parameters": {
            "base_name": {
                "type": "string",
                "description": "Name of the base to create"
            },
            "base_description": {
                "type": "string",
                "description": "Description of the base"
            }
        }
    }
)(create_base)

mcp.tool(
    annotations={
        "name": "assign_base_to_space",
        "description": "Assign a base to a space",
        "parameters": {
            "space_id": {
                "type": "string",
                "description": "ID of the space to assign the base to"
            },
            "base_id": {
                "type": "string",
                "description": "ID of the base to assign"
            }
        }
    }
)(assign_base_to_space)

mcp.tool(
    annotations={
        "name": "create_spaces",
        "description": "Create a new space",
        "parameters": {
            "space_name": {
                "type": "string",
                "description": "Name of the space"
            },
            "space_description": {
                "type": "string",
                "description": "Description of the space"
            }
        }
    }
)(create_spaces)





def main():
    """Main function for running the huuh server."""
    load_dotenv()
    logger.info("Starting huuh MCP server...")

    try:
        # Run the MCP server with Streamable HTTP transport
        sock = socket.socket()
        sock.bind(('', 0))
        port_number = sock.getsockname()[1]
        parser = argparse.ArgumentParser(description="Run MCP Streamable HTTP based server")
        parser.add_argument("--port", type=int, default=port_number, help="Localhost port to listen on")
        args = parser.parse_args()

        logger.info(f"Starting MCP server with Streamable HTTP transport on port {args.port} at path /mcp")
        mcp.run(transport="stdio")
        # await mcp.run_async(transport="http",
        #                     port=os.getenv('PORT', args.port),
        #                     path="/mcp")
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Error running MCP server: {str(e.__repr__())}: {tb}")


if __name__ == "__main__":
    main()
