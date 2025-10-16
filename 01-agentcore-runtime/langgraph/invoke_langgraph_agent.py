import json
import boto3
import sys

def invoke_agent(agent_arn, prompt, region='us-east-1'):
    """Invoke LangGraph agent"""
    client = boto3.client('bedrock-agentcore', region_name=region)
    
    response = client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        qualifier="DEFAULT",
        payload=json.dumps({"prompt": prompt})
    )
    
    content = []
    for chunk in response.get("response", []):
        content.append(chunk.decode('utf-8'))
    
    return json.loads(''.join(content))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python invoke_langgraph_agent.py <AGENT_ARN> <PROMPT>")
        sys.exit(1)
    
    agent_arn = sys.argv[1]
    prompt = sys.argv[2]
    
    result = invoke_agent(agent_arn, prompt)
    print(result)
