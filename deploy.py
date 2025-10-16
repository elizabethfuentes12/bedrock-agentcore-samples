#!/usr/bin/env python3

import os
import sys
from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session

def deploy(agent_path, execution_role_arn=None):
    """Deploy agent from specified path"""
    if not os.path.exists(agent_path):
        print(f"Error: Agent path {agent_path} does not exist")
        sys.exit(1)
    
    # Change to agent directory
    original_dir = os.getcwd()
    os.chdir(agent_path)
    
    try:
        boto_session = Session()
        region = boto_session.region_name
        
        agentcore_runtime = Runtime()
        agent_name = os.path.basename(agent_path)
        
        print(f"Deploying {agent_name} from {agent_path} to {region}...")
        
        # Configure based on execution role
        config_params = {
            "entrypoint": "my_agent.py",
            "auto_create_ecr": True,
            "requirements_file": "requirements.txt",
            "region": region,
            "agent_name": agent_name,
            "non_interactive": True
        }
        
        if execution_role_arn:
            config_params["execution_role"] = execution_role_arn
            config_params["auto_create_execution_role"] = False
        else:
            config_params["auto_create_execution_role"] = True
        
        agentcore_runtime.configure(**config_params)
        
        # Launch
        result = agentcore_runtime.launch()
        print(f"✅ Agent deployed: {result.agent_arn}")
        
        return result
        
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy.py <AGENT_PATH> [EXECUTION_ROLE_ARN]")
        sys.exit(1)
    
    agent_path = sys.argv[1]
    execution_role_arn = sys.argv[2] if len(sys.argv) > 2 else None
    
    deploy(agent_path, execution_role_arn)
