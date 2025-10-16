#!/usr/bin/env python3

from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session

def deploy():
    """Deploy the LangGraph agent"""
    boto_session = Session()
    region = boto_session.region_name
    
    agentcore_runtime = Runtime()
    agent_name = "langgraph_agent"
    
    print(f"Deploying LangGraph agent to {region}...")
    
    # Configure
    agentcore_runtime.configure(
        entrypoint="my_agent_langgraph.py",
        auto_create_execution_role=True,
        auto_create_ecr=True,
        requirements_file="requirements.txt",
        region=region,
        agent_name=agent_name
    )
    
    # Launch
    result = agentcore_runtime.launch()
    print(f"✅ Agent deployed: {result.agent_arn}")
    
    return result

if __name__ == "__main__":
    deploy()
