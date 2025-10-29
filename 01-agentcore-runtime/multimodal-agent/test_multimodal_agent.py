#!/usr/bin/env python3
import boto3
import json
import uuid
import sys
import os

def test_multimodal_agent(agent_arn, file_path):
    client = boto3.client('bedrock-agentcore', region_name="us-west-2")
    session_id = str(uuid.uuid4())
    
    # Detect file type and create appropriate prompt
    file_ext = file_path.split('.')[-1].lower()
    
    if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        prompt = f"Analyze the image {file_path} in detail and describe everything you observe"
    elif file_ext in ['mp4', 'mov', 'avi', 'mkv', 'webm']:
        prompt = f"Analyze the video {file_path} and describe in detail the actions and scenes you observe"
    elif file_ext == 'pdf':
        prompt = f"Summarize the content of the document {file_path}"
    else:
        print(f"Unsupported file type: {file_ext}")
        return
    
    # First request - analyze the file
    print(f"🔍 Analyzing {file_ext.upper()} file: {file_path}")
    print(f"❓ Question: {prompt}")
    print("=" * 80)
    
    payload = json.dumps({"prompt": prompt}).encode()
    
    response = client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        runtimeSessionId=session_id,
        payload=payload
    )
    
    print("💬 Response:")
    process_response(response)
    
    # Follow-up request to test conversation memory
    followup_question = "What did you just analyze? What was the main content?"
    print("\n" + "=" * 80)
    print("🧠 Testing conversation memory...")
    print(f"❓ Question: {followup_question}")
    print("=" * 80)
    
    followup_payload = json.dumps({"prompt": followup_question}).encode()
    
    followup_response = client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        runtimeSessionId=session_id,
        payload=followup_payload
    )
    
    print("💬 Response:")
    process_response(followup_response)

def process_response(response):
    if "text/event-stream" in response.get("contentType", ""):
        content = []
        for line in response["response"].iter_lines(chunk_size=10):
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    line = line[6:]
                    content.append(line)
        print("\n".join(content))
    elif response.get("contentType") == "application/json":
        content = []
        for chunk in response.get("response", []):
            content.append(chunk.decode('utf-8'))
        result = json.loads(''.join(content))
        
        # Extract and format the response text
        if 'result' in result and 'content' in result['result']:
            for content_item in result['result']['content']:
                if 'text' in content_item:
                    print(content_item['text'])
        else:
            print(result)
    else:
        print(response)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_multimodal_agent.py <AGENT_ARN> <FILE_PATH>")
        sys.exit(1)
    
    agent_arn = sys.argv[1]
    file_path = sys.argv[2]
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    test_multimodal_agent(agent_arn, file_path)
