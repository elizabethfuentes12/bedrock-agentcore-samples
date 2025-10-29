# Multimodal Agent for AgentCore Runtime

Multimodal agent that can process images, documents, and videos using Strands Agents, based on the [multi-understanding.ipynb](https://github.com/strands-agents/strands-agent-samples/blob/main/notebook/multi-understanding.ipynb) example.

## Features

- **Image Processing**: PNG, JPEG, GIF, WebP
- **Document Processing**: PDF, CSV, DOCX, XLS, XLSX  
- **Video Processing**: MP4, MOV, AVI, MKV, WebM
- **Session Management**: Maintains conversation context
- **Streaming**: Real-time responses

## Files

- `multimodal_agent.py` - Main agent with AgentCore integration
- `video_reader.py` - Video analysis tool
- `test_multimodal_agent.py` - Complete test suite
- `README.md` - This documentation

## Local Usage

1. **Install dependencies**:
```bash
pip install strands-agents strands-agents-tools boto3
```

2. **Test locally**:
```bash
python multimodal_agent.py
```

3. **In another terminal, test with curl**:
```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What can you do with multimodal content?"}'
```

## AgentCore Deployment

1. **Configure the agent**:
```bash
agentcore configure -e multimodal_agent.py
```

2. **Launch to production**:
```bash
agentcore launch
```

## Testing

### Basic Tests (Text Only)
```bash
python test_multimodal_agent.py "AGENT_ARN"
```

### Multimodal Tests (With Image)
```bash
python test_multimodal_agent.py "AGENT_ARN" "path/to/image.jpg"
```

### Complete Example
```bash
python test_multimodal_agent.py \
  "arn:aws:bedrock-agentcore:us-west-2:123456789012:agent-runtime/ABCDEFGHIJ" \
  "../data-sample/diagram.jpg"
```

## Agent Capabilities

### Image Analysis
- Detailed visual content description
- Object and element identification
- Diagram and architecture analysis

### Document Processing
- PDF text extraction
- Spreadsheet analysis
- Content summarization

### Video Analysis
- Scene and action description
- Visual element identification
- Temporal content analysis

## Model Configuration

The agent uses by default:
- **Model**: `us.anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Region**: `us-west-2`
- **Streaming**: Disabled

## Session Management

AgentCore Runtime provides automatic session management:
- **Maximum duration**: 8 hours
- **Idle timeout**: 15 minutes
- **Isolation**: Each session in dedicated microVM

## Response Structure

```json
{
  "result": {
    "role": "assistant",
    "content": [
      {
        "text": "Agent response..."
      }
    ]
  }
}
```

## Error Handling

The test suite handles:
- `ValidationException`: Invalid parameters
- `ResourceNotFoundException`: Agent not found
- `AccessDeniedException`: Insufficient permissions
- `ThrottlingException`: Rate limits

## Limits

- **Maximum payload**: 100 MB
- **Supported formats**: See features list
- **Recommended region**: us-west-2 (for video_reader)

## Cleanup

To remove the deployed agent:
```bash
agentcore destroy
```
