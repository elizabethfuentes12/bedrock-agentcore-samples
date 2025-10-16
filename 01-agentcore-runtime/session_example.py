import json
import uuid
import boto3
import os
import sys
import time

def session_conversation_example(agent_arn, region='us-west-2'):
    """Demonstrate session-aware conversation with AgentCore Runtime"""
    
    # Initialize client
    client = boto3.client('bedrock-agentcore', region_name=region)
    
    # Generate unique session ID (minimum 33 characters)
    session_id = f"user-demo-conversation-{str(uuid.uuid4())}"
    
    print(f"Starting conversation with session: {session_id}")
    print("=" * 60)
    
    # First message - establish context
    print("Message 1: Setting context...")
    response1 = client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        runtimeSessionId=session_id,
        payload=json.dumps({"prompt": "My name is Alice and I'm learning about AWS. Can you help me understand what EC2 is?"}).encode(),
        qualifier="DEFAULT"
    )
    
    result1 = json.loads(''.join([chunk.decode('utf-8') for chunk in response1.get("response", [])]))
    print(f"Agent: {result1.get('result', {}).get('content', [{}])[0].get('text', 'No response')}")
    print()
    
    # Wait a moment
    time.sleep(2)
    
    # Second message - reference previous context
    print("Message 2: Building on context...")
    response2 = client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        runtimeSessionId=session_id,  # Same session ID
        payload=json.dumps({"prompt": "Thanks! Can you also explain how EC2 pricing works? Remember, I'm still learning."}).encode(),
        qualifier="DEFAULT"
    )
    
    result2 = json.loads(''.join([chunk.decode('utf-8') for chunk in response2.get("response", [])]))
    print(f"Agent: {result2.get('result', {}).get('content', [{}])[0].get('text', 'No response')}")
    print()
    
    # Wait a moment
    time.sleep(2)
    
    # Third message - test memory
    print("Message 3: Testing session memory...")
    response3 = client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        runtimeSessionId=session_id,  # Same session ID
        payload=json.dumps({"prompt": "What was my name again? And what topic were we discussing?"}).encode(),
        qualifier="DEFAULT"
    )
    
    result3 = json.loads(''.join([chunk.decode('utf-8') for chunk in response3.get("response", [])]))
    print(f"Agent: {result3.get('result', {}).get('content', [{}])[0].get('text', 'No response')}")
    print()
    
    print("=" * 60)
    print(f"Session completed: {session_id}")
    print("Note: Session will remain active for 15 minutes (idle timeout)")
    print("      or up to 8 hours (maximum lifetime)")

def main():
    # Get variables from environment or command line
    agent_arn = os.getenv('AGENT_ARN')
    region = os.getenv('AWS_REGION', 'us-west-2')
    
    # Override with command line arguments if provided
    if len(sys.argv) > 1:
        agent_arn = sys.argv[1]
    if len(sys.argv) > 2:
        region = sys.argv[2]
    
    if not agent_arn:
        print("Usage: python session_example.py <AGENT_ARN> [REGION]")
        print("Or set AGENT_ARN environment variable")
        sys.exit(1)
    
    print(f"Testing session management with agent: {agent_arn}")
    print(f"Region: {region}")
    print("-" * 50)
    
    try:
        session_conversation_example(agent_arn, region)
    except Exception as e:
        print(f"Error during session test: {e}")

if __name__ == "__main__":
    main()
