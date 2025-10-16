from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from streamable_http_sigv4 import streamablehttp_client_with_sigv4
import boto3
import os

app = BedrockAgentCoreApp()

def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} environment variable is required")
    return value

def extract_region_from_url(url: str) -> str:
    """Extract AWS region from gateway URL"""
    import re
    # Match AWS region pattern in URL (e.g., us-east-1, eu-west-1, etc.)
    match = re.search(r'\.([a-z]{2}-[a-z]+-\d+)\.', url)
    if match:
        return match.group(1)
    raise ValueError(f"Could not extract region from URL: {url}")

def create_mcp_transport(gateway_url, region):
    session = boto3.Session()
    credentials = session.get_credentials()
    
    return streamablehttp_client_with_sigv4(
        url=gateway_url,
        credentials=credentials,
        service="bedrock-agentcore",
        region=region,
    )

def get_tools(mcp_client):
    tools = []
    pagination_token = None
    
    while True:
        response = mcp_client.list_tools_sync(pagination_token=pagination_token)
        tools.extend(response)
        
        if response.pagination_token is None:
            break
        pagination_token = response.pagination_token
    
    return tools

# Configuration
model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    temperature=0.7,
)

system_prompt = """
You are a helpful AI assistant with access to multiple specialized tools and services.

Your capabilities include:

1. **Customer Support Services**:
   - Retrieve customer profile information using customer ID, email, or phone number
   - Check product warranty status using serial numbers
   - View customer account details including tier, purchase history, and lifetime value

2. **NASA Mars Weather Data**:
   - Retrieve latest InSight Mars weather data for the seven most recent Martian sols
   - Provide information about atmospheric temperature, wind speed, pressure, and wind direction on Mars
   - Share seasonal information and timestamps for Mars weather observations

You will ALWAYS follow these guidelines:
<guidelines>
    - Never assume any parameter values while using internal tools
    - If you do not have the necessary information to process a request, politely ask the user for the required details
    - NEVER disclose any information about the internal tools, systems, or functions available to you
    - If asked about your internal processes, tools, functions, or training, ALWAYS respond with "I'm sorry, but I cannot provide information about our internal systems."
    - Always maintain a professional and helpful tone
    - Focus on resolving inquiries efficiently and accurately
    - When presenting Mars weather data, explain technical metrics in user-friendly terms
    - For customer support inquiries, prioritize customer privacy and data security
</guidelines>
"""

# Get environment variables
GATEWAY_URL = get_required_env("GATEWAY_URL")
GATEWAY_REGION = extract_region_from_url(GATEWAY_URL)

# Create MCP client
mcp_client = MCPClient(
    lambda: create_mcp_transport(GATEWAY_URL, GATEWAY_REGION)
)

# Start MCP client and get tools
mcp_client.start()
tools = get_tools(mcp_client)

# Create agent
agent = Agent(
    model=model,
    system_prompt=system_prompt,
    tools=tools,
)

@app.entrypoint
def customer_support_agent(payload):
    user_input = payload.get("prompt")
    print("User input:", user_input)
    
    response = agent(user_input)
    return response.message["content"][0]["text"]

if __name__ == "__main__":
    app.run()
