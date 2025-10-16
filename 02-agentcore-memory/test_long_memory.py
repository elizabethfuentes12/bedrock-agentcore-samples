import json
import uuid
import boto3
import os
import sys
import time

def test_long_memory(agent_arn, region=None):
    """Test long-term memory across different sessions"""
    
    # Extract region from ARN if not provided
    if not region:
        region = agent_arn.split(':')[3]
    
    # Initialize client
    client = boto3.client('bedrock-agentcore', region_name=region)
    
    # Generate session IDs
    session_1 = str(uuid.uuid4())
    session_2 = str(uuid.uuid4())
    
    print(f"Testing long-term memory across sessions")
    print(f"Region: {region}")
    print("-" * 50)
    
    try:
        # Session 1: Store user information
        print(f"Session 1: {session_1}")
        print("Storing user preferences...")
        
        payload1 = json.dumps({"prompt": "My name is Sarah and I'm a software engineer. I prefer Python over JavaScript."}).encode()
        
        response1 = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_1,
            payload=payload1,
            qualifier="DEFAULT"
        )
        
        content1 = []
        for chunk in response1.get("response", []):
            content1.append(chunk.decode('utf-8'))
        
        result1 = json.loads(''.join(content1))
        print(f"Agent: {result1.get('response', 'No response')}")
        print()
        
        # Wait for long-term memory extraction
        print("Waiting 25 seconds for long-term memory extraction...")
        time.sleep(25)
        
        # Session 2: Test memory recall
        print(f"Session 2: {session_2}")
        print("Testing cross-session memory recall...")
        
        payload2 = json.dumps({"prompt": "What do you remember about me? What's my name and what do I prefer?"}).encode()
        
        response2 = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_2,  # Different session
            payload=payload2,
            qualifier="DEFAULT"
        )
        
        content2 = []
        for chunk in response2.get("response", []):
            content2.append(chunk.decode('utf-8'))
        
        result2 = json.loads(''.join(content2))
        print(f"Agent: {result2.get('response', 'No response')}")
        
        print("\n✓ Long-term memory test completed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    agent_arn = os.getenv('AGENT_ARN')
    region = os.getenv('AWS_REGION')
    
    if len(sys.argv) > 1:
        agent_arn = sys.argv[1]
    if len(sys.argv) > 2:
        region = sys.argv[2]
    
    if not agent_arn:
        print("Usage: python test_long_memory.py <AGENT_ARN> [REGION]")
        print("Or set AGENT_ARN environment variable")
        sys.exit(1)
    
    test_long_memory(agent_arn, region)

if __name__ == "__main__":
    main()
