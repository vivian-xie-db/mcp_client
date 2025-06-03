from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
import asyncio
from databricks.sdk.core import Config

config = Config(profile="e2-demo-field-eng")
token = config.oauth_token().access_token
headers = {"Authorization": f"Bearer {token}"}
url = "https://genie-app-vivian-1444828305810485.aws.databricksapps.com/api/mcp/"
transport = StreamableHttpTransport(
    url=url,
    headers=headers
)
client = Client(transport)
async def main():
    async with client:
        result = await client.list_resources()
        print(result)
        response = await client.read_resource("resource://agent_cards/genie_supply_chain_agent")
        print(response)
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        result = await client.call_tool(
            name="genie-query",
            arguments={"query": "List top 3 distribution centers"}
        )
        print(result)
        
asyncio.run(main())
