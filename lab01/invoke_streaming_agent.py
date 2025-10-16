import json
import uuid
import boto3
import os
import sys

def invoke_streaming_agent(agent_arn, prompt, region=None):
    """Invoke AgentCore Runtime agent with streaming response"""
    
    # Extract region from ARN if not provided
    if not region:
        region = agent_arn.split(':')[3]
    
    # Initialize the Amazon Bedrock AgentCore client
    client = boto3.client('bedrock-agentcore', region_name=region)
    
    # Prepare the payload
    payload = json.dumps({"prompt": prompt}).encode()
    
    try:
        # Invoke the agent with streaming
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=str(uuid.uuid4()),
            payload=payload,
            qualifier="DEFAULT"
        )
        
        print("Streaming response:")
        print("-" * 30)
        
        # Process streaming response
        for chunk in response.get("response", []):
            chunk_data = chunk.decode('utf-8')
            try:
                parsed_chunk = json.loads(chunk_data)
                if 'content' in parsed_chunk:
                    print(parsed_chunk['content'], end='', flush=True)
                else:
                    print(chunk_data, end='', flush=True)
            except json.JSONDecodeError:
                print(chunk_data, end='', flush=True)
        
        print("\n" + "-" * 30)
        print("Streaming completed")
        
    except Exception as e:
        print(f"Error invoking streaming agent: {e}")
        return None

def main():
    # Get variables from environment or command line
    agent_arn = os.getenv('STREAMING_AGENT_ARN')
    prompt = os.getenv('PROMPT', 'Tell me a story about AI agents')
    region = os.getenv('AWS_REGION')
    
    # Override with command line arguments if provided
    if len(sys.argv) > 1:
        agent_arn = sys.argv[1]
    if len(sys.argv) > 2:
        prompt = sys.argv[2]
    if len(sys.argv) > 3:
        region = sys.argv[3]
    
    if not agent_arn:
        print("Usage: python invoke_streaming_agent.py <AGENT_ARN> [PROMPT] [REGION]")
        print("Or set STREAMING_AGENT_ARN environment variable")
        sys.exit(1)
    
    # Extract region from ARN if not provided
    if not region:
        region = agent_arn.split(':')[3]
    
    print(f"Invoking streaming agent: {agent_arn}")
    print(f"Prompt: {prompt}")
    print(f"Region: {region}")
    print("=" * 50)
    
    invoke_streaming_agent(agent_arn, prompt, region)

if __name__ == "__main__":
    main()
