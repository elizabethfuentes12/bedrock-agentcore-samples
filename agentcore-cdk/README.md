# Amazon Bedrock AgentCore CDK Sample

Deploy production-ready AI agents using Amazon Bedrock AgentCore Runtime with AWS CDK.

![Architecture Diagram](./agent-mcp-cdk.drawio.svg)

## Overview

This project demonstrates how to deploy a complete AI agent infrastructure using AWS CDK, featuring:

- **AgentCore Runtime**: Containerized agent with persistent sessions
- **AgentCore Gateway**: MCP (Model Context Protocol) gateway for tool orchestration
- **Lambda Tools**: Serverless functions for AWS blog search and web content extraction
- **IAM Security**: Proper isolation and least-privilege access


## Main Stack (`agentcore_cdk_stack.py`)

The core CDK stack deploy all components:

```python
class AgentcoreCdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Lambda functions for tools
        self.lambda_functions = Lambdas(self, "L")

        # Create MCP Gateway
        self.agent_core_gateway = AgentCoreGateway(
            self, "ACG", 
            AGENTCORE_GATEWAY_NAME, 
            GATEWAY_DESCRIPTION
        )

        # Register Lambda tools with the gateway
        self.agent_core_gateway.add_lambda_target(
            extract_target.get("name"),
            extract_target.get("description"),
            extract_target.get("input_schema"),
            self.lambda_functions.web_extract_tool.function_arn,
        )
        self.agent_core_gateway.add_lambda_target(
            aws_blogs_search_target.get("name"),
            aws_blogs_search_target.get("description"),
            aws_blogs_search_target.get("input_schema"),
            self.lambda_functions.aws_blog_search.function_arn,
        )

        # Create AgentCore Runtime with container
        self.agent_core_runtime = AgentCoreRuntime(self, "AgentCore")
        
        env_vars = dict(
            GATEWAY_URL=self.agent_core_gateway.gateway.attr_gateway_url,
            MODEL_ID=MODEL_ID
        )
        
        self.agent_core_runtime.create_runtime(
            AGENT_RUNTIME_NAME, 
            AGENT_RUNTIME_DESCRIPTION, 
            AGENT_DIRECTORY, 
            env_vars
        )
```

**Key Features:**
- Integrates Lambda functions as MCP tools
- Passes gateway URL to runtime via environment variables
- MCP invocation is done using Runtime IAM Role (no need for JWT)
- Outputs agent ARN for invocation

## Deployment Guide

### Prerequisites

- AWS CLI configured with appropriate credentials
- Python 3.13+
- aws-cdk
- Docker (for container builds)

### Step 1: Environment Setup

```bash
# Clone the repository
cd agentcore-cdk

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate.bat  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Parameters

Edit `agentcore_cdk_stack.py` to customize:

```python
# Model Configuration
MODEL_ID = "global.anthropic.claude-haiku-4-5-20251001-v1:0"  # Change model here

# Gateway Configuration
AGENTCORE_GATEWAY_NAME = "aws-blogs-mcp"  # Your gateway name
GATEWAY_DESCRIPTION = "AWS Blogs search and page extraction"

# Runtime Configuration
AGENT_RUNTIME_NAME = "AWS_Researcher"  # Your agent name
AGENT_RUNTIME_DESCRIPTION = "Your AWS Researcher using curated Blogs"
AGENT_DIRECTORY = "./agent_container"  # Path to agent code
```

### Step 3: Bootstrap CDK (First Time Only)

```bash
cdk bootstrap
```

### Step 4: Deploy

```bash
# Deploy stack
cdk deploy
```

### Step 5: Get Agent ARN

After deployment, note the output:

```
Outputs:
AgentcoreCdkStack.AgentArn = arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/AWS_Researcher-xxxxx
```

### Step 6: Test Your Agent

Use the provided Jupyter notebook `test.deployed.agent.ipynb`:

```python
import boto3
import json
from uuid import uuid4

agent_core_client = boto3.client('bedrock-agentcore')
agent_arn = 'YOUR_AGENT_ARN_FROM_OUTPUT'

# Invoke agent
rsession_id=str(uuid4())
payload = json.dumps({"prompt": "search about deploying gen ai agents to production"}).encode()
invoke_agent_core(agent_arn, payload, session_id)
```

Look at the latest invocation sample at [test.deployed.agent.ipynb](test.deployed.agent.ipynb)

## Customization Guide

### Adding New Tools

1. **Create Lambda function** in `lambdas/code/your_tool/`
2. **Add to project_lambdas.py**:
```python
self.your_tool = aws_lambda.Function(
    self, "YourTool",
    code=aws_lambda.Code.from_asset("./lambdas/code/your_tool/"),
    handler="lambda_function.lambda_handler",
    **BASE_LAMBDA_CONFIG,
)
```

3. **Define schema** in `target_definitions.py`:
```python
your_tool_target = dict(
    description="Your tool description",
    input_schema={
        "properties": {"param": {"type": "string"}},
        "required": ["param"],
        "type": "object",
    },
    name="your_tool",
)
```

4. **Register in stack**:
```python
self.agent_core_gateway.add_lambda_target(
    your_tool_target.get("name"),
    your_tool_target.get("description"),
    your_tool_target.get("input_schema"),
    self.lambda_functions.your_tool.function_arn,
)
```

### Changing the Model

Edit `MODEL_ID` in `agentcore_cdk_stack.py`:


### Modifying Agent Logic

Edit files in `agent_container/`:
- `agent_class.py`: Agent reasoning logic
- `runtime_agent.py`: HTTP server and invocation handling
- `requirements.txt`: Python dependencies


## License

This project is licensed under the MIT-0 License.
