from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
import asyncio
from databricks.sdk.core import Config

config = Config()
token = config.oauth_token().access_token
url = "https://app_url.aws.databricksapps.com/api/mcp/"
transport = StreamableHttpTransport(
    url=url,
    headers={"Authorization": f"Bearer {token}"}
)

client = Client(transport)
async def main():
    async with client:
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        result = await client.call_tool(
            name="genie-query",
            arguments={"query": "List top 3 distribution centers"}
        )
        print(result)
        

asyncio.run(main())
