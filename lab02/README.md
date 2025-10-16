# Amazon Bedrock AgentCore Memory Lab

Add intelligent memory capabilities to AI agents with Amazon Bedrock AgentCore Memory.

## What is AgentCore Memory?

Amazon Bedrock AgentCore Memory is a fully managed service that gives your AI agents the ability to remember past interactions, enabling them to provide more intelligent, context-aware, and personalized conversations.

### AgentCore Services

- **AgentCore Runtime** - Serverless execution with auto-scaling and session management
- **AgentCore Identity** - Secure credential management for API keys and tokens  
- **AgentCore Memory** ⭐ - State persistence and conversation history
- **AgentCore Code Interpreter** - Secure code execution sandbox
- **AgentCore Browser** - Cloud browser automation
- **AgentCore Gateway** - API management and tool discovery
- **AgentCore Observability** - Monitoring, tracing, and debugging

## This Lab: AgentCore Memory

This project demonstrates **AgentCore Memory** with two types of memory:

- **Short-term memory** - Conversation context within sessions
- **Long-term memory** - Persistent knowledge across sessions

## Memory Types

### Short-term Memory
Captures turn-by-turn interactions within a single session. Agents maintain immediate context without requiring users to repeat information.

**Example**: When a user asks, "What's the weather like in Seattle?" and follows up with "What about tomorrow?", the agent relies on recent conversation history to understand that "tomorrow" refers to the weather in Seattle.

### Long-term Memory
Automatically extracts and stores key insights from conversations across multiple sessions, including user preferences, important facts, and session summaries.

**Example**: If a customer mentions they prefer window seats during flight booking, the agent stores this preference in long-term memory. In future interactions, the agent can proactively offer window seats.

## Quick Start

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Test locally**
```bash
python my_agent_memory.py
```

3. **Deploy to production**
```bash
# Configure with memory enabled
agentcore configure -e my_agent_memory.py
# Select 'yes' for memory
# Select 'yes' for long-term memory extraction

# Launch to production
agentcore launch
```

4. **Test memory functionality**

The test scripts use boto3 to programmatically invoke your deployed agent via the `InvokeAgentRuntime` operation. This allows automated testing of memory capabilities across different sessions.

```bash
# Test short-term memory (within session)
python test_short_memory.py "AGENT_ARN"

# Test long-term memory (across sessions)
python test_long_memory.py "AGENT_ARN"

# Or using environment variables
export AGENT_ARN="your-agent-arn"
python test_short_memory.py
python test_long_memory.py
```

**Boto3 Integration**: The tests use the AWS SDK to call `bedrock-agentcore:InvokeAgentRuntime`, requiring your agent ARN and appropriate permissions. Each test creates unique session IDs to simulate different user interactions.

## Memory Configuration

The agent uses AgentCore Memory SDK for integration with Strands Agents. For complete SDK documentation, see: https://github.com/aws/bedrock-agentcore-sdk-python/tree/main/src/bedrock_agentcore/memory

### Basic Memory Setup
```python
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig

# Create memory client
client = MemoryClient(region_name="us-east-1")

# Create memory store
basic_memory = client.create_memory(
    name="BasicTestMemory",
    description="Basic memory for testing short-term functionality"
)

# Configure memory with retrieval settings
memory_config = AgentCoreMemoryConfig(
    memory_id=basic_memory.get('id'),
    session_id=session_id,
    actor_id=actor_id,
    retrieval_config={
        f"/users/{actor_id}/facts": RetrievalConfig(top_k=3, relevance_score=0.5),
        f"/users/{actor_id}/preferences": RetrievalConfig(top_k=3, relevance_score=0.5)
    }
)
```

### Memory Integration with Strands Agents
```python
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# Create agent with memory
agent = Agent(
    session_manager=AgentCoreMemorySessionManager(memory_config, REGION),
    system_prompt="You are a helpful assistant with memory. Remember user preferences and facts across conversations."
)
```

## What's Included

- [`my_agent_memory.py`](my_agent_memory.py) - Agent with AgentCore Memory integration
- [`test_short_memory.py`](test_short_memory.py) - Test short-term memory within sessions
- [`test_long_memory.py`](test_long_memory.py) - Test long-term memory across sessions
- [`requirements.txt`](requirements.txt) - Required packages for AgentCore Memory

## The invoke Function

The `invoke` function is the main entry point for your AgentCore agent. It:

- Receives user prompts and context from AgentCore Runtime
- Extracts session and actor IDs for memory management
- Creates or retrieves the agent instance with memory configuration
- Processes the user message and returns the response

```python
@app.entrypoint
def invoke(payload, context):
    """AgentCore Runtime entry point with lazy-loaded agent"""
    # Extract user prompt
    prompt = payload.get("prompt", "Hello!")
    
    # Get session/actor info for memory
    actor_id = context.request_headers.get('X-Amzn-Bedrock-AgentCore-Runtime-Custom-Actor-Id', 'user')
    session_id = context.session_id
    
    # Get agent with memory
    agent = get_or_create_agent(actor_id, session_id)
    
    # Process and return response
    result = agent(prompt)
    return {"response": result.message}
```

## Memory Testing

### Short-term Memory Test
```bash
python test_short_memory.py "AGENT_ARN"

# This test:
# 1. Stores user info in a session
# 2. Asks agent to recall info in same session
# 3. Verifies context is maintained
```

### Long-term Memory Test
```bash
python test_long_memory.py "AGENT_ARN"

# This test:
# 1. Stores user preferences in session 1
# 2. Waits 25 seconds for LTM extraction
# 3. Tests recall in different session 2
# 4. Verifies cross-session memory
```

## Key Benefits

- **Contextual conversations** - Agents remember what was discussed
- **Personalized experiences** - User preferences persist across sessions
- **Reduced repetition** - Users don't need to re-explain context
- **Intelligent insights** - Automatic extraction of important information
- **Scalable architecture** - Fully managed service handles complexity

## Prerequisites

- AWS account with appropriate permissions
- Python 3.10+ environment
- AWS CLI configured
- AgentCore Memory service enabled

## Clean Up

```bash
agentcore destroy
```

*This lab focuses on AgentCore Memory. Combine with AgentCore Runtime for complete production-ready AI agents with persistent memory.*
