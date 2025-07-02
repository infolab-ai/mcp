## Docker

docker build . -f smithery.Dockerfile -t huuh_mcp:local && docker run huuh_mcp:local --network

## run locally

uv --directory C:\coding_challanges\Infolab\repos\mcp\ run -m huuh_mcp.server --env-file C:\coding_challanges\Infolab\repos\mcp\huuh_mcp\.env

## comparable servers

https://github.com/ScrapeGraphAI/scrapegraph-mcp/blob/main/Dockerfile
https://github.com/nickclyde/duckduckgo-mcp-server/blob/main/Dockerfile