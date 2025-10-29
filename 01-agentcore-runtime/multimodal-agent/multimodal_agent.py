from bedrock_agentcore import BedrockAgentCoreApp
from strands.models import BedrockModel
from strands import Agent
from strands_tools import image_reader, file_read
from video_reader import video_reader
import boto3

app = BedrockAgentCoreApp()

# Multimodal system prompt
MULTIMODAL_SYSTEM_PROMPT = """You are a helpful assistant that can process documents, images, and videos. 
Analyze their contents and provide relevant information.

You can:
1. For PNG, JPEG/JPG, GIF, or WebP formats use image_reader to process file
2. For PDF, csv, docx, xls or xlsx formats use file_read to process file  
3. For MP4, MOV, AVI, MKV, WebM formats use video_reader to process file

When displaying responses:
- Format answers in a human-readable way
- Highlight important information
- Handle errors appropriately
- Convert technical terms to user-friendly language
- Always reply in the original user language
"""

# Global agent variable
multimodal_agent = None

def get_agent():
    """Initialize agent if not already created"""
    global multimodal_agent
    if multimodal_agent is None:
        session = boto3.Session(region_name='us-west-2')
        bedrock_model = BedrockModel(
            model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            boto_session=session,
            streaming=False
        )
        
        multimodal_agent = Agent(
            system_prompt=MULTIMODAL_SYSTEM_PROMPT,
            tools=[image_reader, file_read, video_reader],
            model=bedrock_model
        )
    return multimodal_agent

@app.entrypoint
def invoke(payload):
    """Multimodal AI agent function"""
    user_message = payload.get("prompt", "Hello! How can I help you analyze images, documents, or videos today?")
    agent = get_agent()
    result = agent(user_message)
    return {"result": result.message}

if __name__ == "__main__":
    app.run()
