# Lab 03: Amazon Bedrock AgentCore Gateway - Customer Services

This lab demonstrates how to use Amazon Bedrock AgentCore Gateway to transform existing AWS Lambda functions into MCP (Model Context Protocol) tools that can be used by AI agents. We focus specifically on a customer services use case.

Based on the [AWS Labs AgentCore Gateway Sample](https://github.com/awslabs/amazon-bedrock-agentcore-samples/blob/main/01-tutorials/02-AgentCore-gateway/04-integration/01-runtime-gateway/04-runtime-gateway.ipynb), this implementation showcases the integration between AgentCore Gateway, AgentCore Runtime, and Strands Agents.

![image](../images/lab_03_architecture.png)

## Architecture
- **AWS Lambda Function**: Handles customer support operations (customer profiles and warranties)
- **Amazon DynamoDB**: Stores customer and warranty data
- **Amazon Bedrock AgentCore Gateway**: Converts Lambda functions into MCP tools
- **Strands Agent**: AI agent that uses tools through the gateway

## Prerequisites

To execute this tutorial you will need:
- Python 3.10+
- AWS credentials configured
- Amazon Bedrock AgentCore SDK
- Strands Agents framework

### Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `strands-agents`: AI agent framework
- `bedrock-agentcore`: Amazon Bedrock AgentCore SDK
- `mcp`: Model Context Protocol client
- `boto3`: AWS SDK for Python

## Project Files

- [`customer_support_app.py`](customer_support_app.py): Main Strands agent application
- [`lambda_function.py`](lambda_function.py): Customer support Lambda function
- [`setup_gateway.py`](setup_gateway.py): Infrastructure deployment and gateway setup (creates both Lambda and NASA targets)
- [`streamable_http_sigv4.py`](streamable_http_sigv4.py): AWS SigV4 authentication module for MCP
- [`cloudformation/customer_support_lambda.yaml`](cloudformation/customer_support_lambda.yaml): AWS infrastructure template
- [`openapi-specs/nasa_mars_insights_openapi.json`](openapi-specs/nasa_mars_insights_openapi.json): NASA API specification for Mars weather data
- [`requirements.txt`](requirements.txt): Project dependencies

## Deployment

### Step 1: Deploy Infrastructure and Gateway
```bash
# Deploy CloudFormation stack, populate data, and create gateway with both targets
python setup_gateway.py
```

This script will:
1. Create the CloudFormation stack with Lambda and DynamoDB resources
2. Populate sample customer and warranty data
3. Create the AgentCore Gateway with AWS_IAM authentication
4. Create Lambda target for customer support operations
5. Create NASA API target for Mars weather data (uses existing credentials or prompts for API key)
6. Output the required configuration values:
   - **🔐 Execution Role ARN**: Required for `bedrock-agentcore configure`
   - **Gateway URL**: Required as `GATEWAY_URL` environment variable for `bedrock-agentcore launch`

### Step 2: Test Locally (Optional)
```bash
export GATEWAY_URL=<your-gateway-url>
python customer_support_app.py
```

### Step 3: Deploy Agent to AgentCore Runtime
```bash
agentcore configure -e customer_support_app.py
```
Remember **🔐 Execution Role ARN** from `setup_gateway.py`

```bash
agentcore launch --env GATEWAY_URL=<gateway-url-from-setup>

# Example gateway URL:
# https://customer-support-gateway-f0yecqihp7.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp

agentcore invoke '{"prompt": "Check warranty for serial MNO33333333, email: eli@amazon.com"}'
agentcore invoke '{"prompt": "Get customer profile for CUST001"}'
```

## Sample Interactions

The agent can handle various customer service scenarios:

```bash
# Warranty check
agentcore invoke '{"prompt": "I have a Gaming Console Pro device, I want to check my warranty status, warranty serial number is MNO33333333, email: jhon@amazon.com"}'

# Customer profile lookup
agentcore invoke '{"prompt": "Can you find the customer profile for john.smith@email.com?"}'

# General inquiry
agentcore invoke '{"prompt": "What information do you need to check a warranty?"}'
```

## Test with invoke_agent.py

You can also invoke the deployed agent programmatically using the AWS SDK. The `invoke_agent.py` script demonstrates how to call the `InvokeAgentRuntime` operation directly.

Based on the [AWS documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-toolkit.html#invoke-programmatically), this script:

1. **Initializes the AgentCore client**: Uses `boto3.client('bedrock-agentcore')`
2. **Prepares the payload**: Encodes the prompt as JSON
3. **Invokes the agent**: Calls `invoke_agent_runtime` with the agent ARN
4. **Processes the response**: Decodes and displays the streaming response

```python
import json
import uuid
import boto3

agent_arn = "Agent ARN"  # Replace with your agent ARN from agentcore launch
prompt = "Check warranty for serial MNO33333333"

# Initialize the Amazon Bedrock AgentCore client
agent_core_client = boto3.client('bedrock-agentcore')

# Prepare the payload
payload = json.dumps({"prompt": prompt}).encode()

# Invoke the agent
response = agent_core_client.invoke_agent_runtime(
    agentRuntimeArn=agent_arn,
    runtimeSessionId=str(uuid.uuid4()),
    payload=payload,
    qualifier="DEFAULT"
)

content = []
for chunk in response.get("response", []):
    content.append(chunk.decode('utf-8'))
print(json.loads(''.join(content)))
```

To use this script:
1. Get the agent ARN from the `agentcore launch` output or from `.bedrock_agentcore.yaml`
2. Replace `"Agent ARN"` with your actual agent ARN
3. Run: `python invoke_agent.py`

**Note**: You need `bedrock-agentcore:InvokeAgentRuntime` permissions to use this approach.

## Code Explanation

### Customer Support Agent Application (`customer_support_app.py`)

#### Environment Configuration and Region Extraction
```python
def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} environment variable is required")
    return value

def extract_region_from_url(url: str) -> str:
    """Extract AWS region from gateway URL"""
    import re
    match = re.search(r'\.([a-z]{2}-[a-z]+-\d+)\.', url)
    if match:
        return match.group(1)
    raise ValueError(f"Could not extract region from URL: {url}")
```

#### SigV4 Authentication Implementation
```python
def create_mcp_transport(gateway_url, region):
    session = boto3.Session()
    credentials = session.get_credentials()
    
    return streamablehttp_client_with_sigv4(
        url=gateway_url,
        credentials=credentials,
        service="bedrock-agentcore",
        region=region,
    )
```

#### Tool Discovery and Pagination
```python
def get_tools(mcp_client):
    """Retrieve complete list of tools, handling pagination"""
    tools = []
    pagination_token = None
    
    while True:
        response = mcp_client.list_tools_sync(pagination_token=pagination_token)
        tools.extend(response)
        
        if response.pagination_token is None:
            break
        pagination_token = response.pagination_token
    
    return tools
```

#### Agent Configuration
```python
# Bedrock model configuration
model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    temperature=0.7,
)

# MCP client setup with SigV4 authentication
mcp_client = MCPClient(
    lambda: create_mcp_transport(GATEWAY_URL, GATEWAY_REGION)
)

# Agent creation with tools from gateway
agent = Agent(
    model=model,
    system_prompt=system_prompt,
    tools=tools,
)
```

#### AgentCore Runtime Entrypoint
```python
@app.entrypoint
def customer_support_agent(payload):
    user_input = payload.get("prompt")
    response = agent(user_input)
    return response.message["content"][0]["text"]
```

### Gateway Setup (`setup_gateway.py`)

#### Gateway Target Configuration
```python
lambda_target_config = {
    "mcp": {
        "lambda": {
            "lambdaArn": lambda_arn,
            "toolSchema": {
                "inlinePayload": [
                    {
                        "name": "get_customer_profile",
                        "description": "Retrieve customer profile using customer ID, email, or phone number",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string"},
                                "email": {"type": "string"},
                                "phone": {"type": "string"},
                            },
                            "required": ["customer_id"],
                        },
                    }
                ]
            },
        }
    }
}
```

## Cleanup

To remove all resources and avoid charges:

### Option 1: Automated Cleanup Script
```bash
# Create cleanup script
cat > cleanup.py << 'EOF'
import boto3

def cleanup_resources():
    # Delete AgentCore Gateway
    agentcore_client = boto3.client('bedrock-agentcore-control')
    gateways = agentcore_client.list_gateways()
    
    for gateway in gateways['items']:
        if gateway['name'] == 'customer-support-gateway':
            agentcore_client.delete_gateway(gatewayIdentifier=gateway['gatewayId'])
            print(f"Deleted gateway: {gateway['gatewayId']}")
    
    # Delete CloudFormation stack
    cf_client = boto3.client('cloudformation')
    cf_client.delete_stack(StackName='customer-support-lambda-stack')
    print("Deleted CloudFormation stack")

if __name__ == "__main__":
    cleanup_resources()
EOF

python cleanup.py
```

### Option 2: Manual Cleanup
```bash
# Delete AgentCore Runtime resources
agentcore destroy 

# Delete Gateway
aws bedrock-agentcore-control list-gateways --query 'items[?name==`customer-support-gateway`].gatewayId' --output text | \
xargs -I {} aws bedrock-agentcore-control delete-gateway --gateway-identifier {}

# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name customer-support-lambda-stack

# Wait for stack deletion
aws cloudformation wait stack-delete-complete --stack-name customer-support-lambda-stack
```

## References

This implementation is based on the following AWS resources:

- [Amazon Bedrock AgentCore Gateway Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
- [Gateway Core Concepts](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-core-concepts.html)
- [AWS Labs AgentCore Gateway Sample Notebook](https://github.com/awslabs/amazon-bedrock-agentcore-samples/blob/main/01-tutorials/02-AgentCore-gateway/04-integration/01-runtime-gateway/04-runtime-gateway.ipynb)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/docs/getting-started/intro)
- [Strands Agents Documentation](https://strandsagents.com/latest/)
- [AWS Labs MCP SigV4 Authentication](https://github.com/awslabs/run-model-context-protocol-servers-with-aws-lambda/tree/main)

The implementation focuses specifically on the customer services use case, extracting and adapting the Lambda function integration patterns from the original notebook example while adding comprehensive deployment automation and code explanations. The critical code components are derived from the AWS Labs tutorial and enhanced for production deployment scenarios.
