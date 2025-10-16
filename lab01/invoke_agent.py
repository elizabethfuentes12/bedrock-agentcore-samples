import json
import uuid
import boto3
import os
import sys

def invoke_agent(agent_arn, prompt, region=None):
    """Invoke AgentCore Runtime agent programmatically"""
    
    # Extract region from ARN if not provided
    if not region:
        region = agent_arn.split(':')[3]
    
    # Initialize the Amazon Bedrock AgentCore client
    client = boto3.client('bedrock-agentcore', region_name=region)
    
    # Prepare the payload
    payload = json.dumps({"prompt": prompt}).encode()
    
    try:
        # Invoke the agent
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=str(uuid.uuid4()),
            payload=payload,
            qualifier="DEFAULT"
        )
        
        # Process response
        content = []
        for chunk in response.get("response", []):
            content.append(chunk.decode('utf-8'))
        
        result = json.loads(''.join(content))
        return result
        
    except Exception as e:
        print(f"Error invoking agent: {e}")
        return None

def main():
    # Get variables from environment or command line
    agent_arn = os.getenv('AGENT_ARN')
    prompt = os.getenv('PROMPT', 'Hello! How can you help me?')
    region = os.getenv('AWS_REGION')
    
    # Override with command line arguments if provided
    if len(sys.argv) > 1:
        agent_arn = sys.argv[1]
    if len(sys.argv) > 2:
        prompt = sys.argv[2]
    if len(sys.argv) > 3:
        region = sys.argv[3]
    
    if not agent_arn:
        print("Usage: python invoke_agent.py <AGENT_ARN> [PROMPT] [REGION]")
        print("Or set AGENT_ARN environment variable")
        sys.exit(1)
    
    # Extract region from ARN if not provided
    if not region:
        region = agent_arn.split(':')[3]
    
    print(f"Invoking agent: {agent_arn}")
    print(f"Prompt: {prompt}")
    print(f"Region: {region}")
    print("-" * 50)
    
    result = invoke_agent(agent_arn, prompt, region)
    
    if result:
        print("Response:")
        print(json.dumps(result, indent=2))
    else:
        print("Failed to get response from agent")

if __name__ == "__main__":
    main()
