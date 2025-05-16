# Infolab MCP Server

This is a Model Context Protocol (MCP) server for integration with the Infolab platform.

## Features

- Authentication with Infolab API using API keys
- Token management with caching
- Server-Sent Events (SSE) transport for remote access
- Example tool implementation

## Installation

1. Clone the repository
2. Create a virtual environment
3. Install dependencies using `pip install -r requirements.txt`
4. Copy `.env.sample` to `.env` and fill in the required variables

```bash
# Clone the repository
git clone <repository-url>
cd infolab-mcp

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.sample .env
# Edit .env with your API key and settings
```

## Configuration

The server requires the following environment variables:

- `INFOLAB_API_URL`: The URL of the Infolab API (default: http://localhost:8000)
- `API_KEY`: Your Infolab API key (obtain from the Infolab user settings page)
- `LOG_LEVEL`: Logging level (default: INFO)
- `TOKEN_CACHE_FILE`: File to cache access tokens (default: token_cache.json)

## Usage

Run the server:

```bash
# Activate virtual environment if not already active
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the server
python -m infolab_mcp.server
```

The server will start on port 8000 and will be accessible via SSE transport.

## Authentication Flow

The MCP server authenticates with the Infolab API using the following flow:

1. When a tool is called, the server checks if a valid access token is cached
2. If a valid token exists, it is used for the API request
3. If no token exists or it has expired, the server exchanges the API key for a new access token
4. The new token is cached for future use
5. The API request is then executed with the valid token

## Adding New Tools

To add a new tool, follow this pattern:

```python
@mcp.tool()
async def your_tool_name(param1: str, param2: int, ctx: Context = None) -> str:
    """
    Tool description.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
        ctx: The MCP context for the current request
        
    Returns:
        The result of the tool operation
    """
    # Authenticate the request
    try:
        user_info = await authenticate(ctx)
        
        # Your tool implementation here
        # ...
        
        return "Result"
    except ValueError as e:
        return f"Authentication error: {str(e)}"
    except Exception as e:
        logger.error(f"Error in your_tool_name: {str(e)}")
        return f"Error: {str(e)}"
```

## Connecting to the MCP Server

MCP clients can connect to the server using the following URL:

```
http://localhost:8000/sse
```

The client must provide a valid Infolab access token in the Authorization header, or the server will attempt to authenticate using its configured API key.
