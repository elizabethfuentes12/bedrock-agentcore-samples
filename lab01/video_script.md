# AgentCore Runtime: Deploy Production AI Agents in 2 Commands
## Episode 1 - Video Script (15 minutes)

---

### INTRO (0:00 - 1:30)

**[HOOK - First 15 seconds]**
"What if I told you that you could deploy a production-ready AI agent to AWS in just 2 commands? No Docker, no Kubernetes, no DevOps nightmares. Just 2 commands and 15 minutes."

**[PAUSE FOR EFFECT]**

"Hi everyone! Welcome to our new series on Amazon Bedrock AgentCore. I'm [Your Name], and today we're starting with AgentCore Runtime - the service that's about to change how you think about deploying AI agents."

**[SHOW TITLE CARD: "AgentCore Runtime - Episode 1"]**

"In this series, we'll explore all the AgentCore services, but today we're focusing on Runtime - the core service that handles serverless execution, auto-scaling, and session management. By the end of this video, you'll have a production agent running on AWS."

---

### PROBLEM SETUP (1:30 - 3:00)

**[SCREEN: Show typical deployment complexity]**

"Let's be honest - deploying AI agents to production is usually a nightmare. You've built this amazing agent on your laptop, it works perfectly, and then... reality hits."

**[LIST ON SCREEN]**
- "3 weeks setting up infrastructure"
- "Docker and Kubernetes configurations"
- "Security policies that make you cry"
- "Scaling configurations you barely understand"
- "Session management... what even is that?"

"Sound familiar? This is exactly why AWS built AgentCore. It takes all this complexity and reduces it to 2 commands."

**[TRANSITION]**
"But before we dive into the demo, let me quickly explain what AgentCore actually is."

---

### AGENTCORE OVERVIEW (3:00 - 5:00)

**[SCREEN: AgentCore Services Diagram]**

"AgentCore is a suite of 7 services designed specifically for AI agents:"

**[ANIMATE EACH SERVICE]**
1. "**AgentCore Runtime** - Today's focus - handles serverless execution and auto-scaling"
2. "**AgentCore Identity** - Secure credential management - we'll dive deep in episode 2"
3. "**AgentCore Memory** - State persistence and conversation history"
4. "**AgentCore Code Interpreter** - Secure code execution sandbox"
5. "**AgentCore Browser** - Cloud browser automation"
6. "**AgentCore Gateway** - API management and tool discovery"
7. "**AgentCore Observability** - Monitoring, tracing, and debugging"

**[HIGHLIGHT RUNTIME]**
"Today we're focusing on Runtime because it's the foundation. This is what actually runs your agents in production."

**[KEY BENEFITS ON SCREEN]**
- "Serverless - no infrastructure management"
- "Auto-scaling - handles traffic spikes automatically"
- "Session isolation - each user gets their own secure environment"
- "Any framework support - Strands, LangGraph, CrewAI, you name it"

---

### ANY FRAMEWORK + ANY MODEL (5:00 - 6:30)

**[SCREEN: Framework logos]**

"Here's what makes AgentCore Runtime special - it supports ANY agent framework. Whether you're using Strands Agents, LangGraph, OpenAI's SDK, Microsoft AutoGen, or CrewAI - they all work."

**[CODE SNIPPET ON SCREEN]**
```python
# Works with any framework
from bedrock_agentcore import BedrockAgentCoreApp
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload, context):
    # Your agent code here
    return {"result": result}
```

"And it's not just frameworks - you can use ANY foundation model. Amazon Bedrock, OpenAI, Anthropic Claude directly, Google Gemini - whatever you prefer."

**[TEASER]**
"Now, when we talk about using external models like OpenAI or Anthropic, you'll need secure API key management. That's where AgentCore Identity comes in - and we'll explore that in detail in our next episode."

---

### DEMO SETUP (6:30 - 8:00)

**[SCREEN: Terminal/IDE]**

"Alright, let's build this thing. I'm going to show you the complete workflow from code to production endpoint."

**[SHOW PROJECT STRUCTURE]**
"Here's what we're building today - a simple AI agent that can have conversations and maintain context across multiple interactions."

**[TERMINAL]**
```bash
# Step 1: Install dependencies
pip install bedrock-agentcore strands-agents bedrock-agentcore-starter-toolkit
```

**[SHOW CODE]**
```python
# my_agent.py - The simplest possible agent
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent()

@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt", "Hello!")
    result = agent(user_message)
    return {"result": result.message}

if __name__ == "__main__":
    app.run()
```

"That's it. 10 lines of code for a production-ready agent."

---

### LOCAL TESTING (8:00 - 9:00)

**[TERMINAL DEMO]**

"First, let's test locally:"

```bash
python my_agent.py
```

**[SHOW AGENT STARTING]**
"Perfect! Now let's test it:"

```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello! Can you help me understand AWS?"}'
```

**[SHOW RESPONSE]**
"Great! Our agent is working locally. Now comes the magic - deploying to production."

---

### DEPLOYMENT MAGIC (9:00 - 11:00)

**[TERMINAL - THE 2 COMMANDS]**

"Here are the 2 commands that deploy this to production:"

**[COMMAND 1]**
```bash
agentcore configure -e my_agent.py
```

**[EXPLAIN WHILE RUNNING]**
"This command analyzes your code, creates the deployment configuration, and sets up all the AWS resources we'll need."

**[SHOW YAML BEING CREATED]**
"See that? It created our configuration file automatically."

**[COMMAND 2]**
```bash
agentcore launch
```

**[EXPLAIN WHILE RUNNING]**
"And this command builds your container using AWS CodeBuild - no Docker needed locally - creates the ECR repository, sets up IAM roles, and deploys to AgentCore Runtime."

**[SHOW BUILD PROGRESS]**
"Look at this - it's building our ARM64 container in the cloud, creating all the security policies, and deploying everything."

**[SHOW SUCCESS MESSAGE WITH ARN]**
"And we're live! Look at that ARN - that's our production endpoint."

---

### SESSION MANAGEMENT DEMO (11:00 - 13:00)

**[TERMINAL]**

"Now let me show you something really cool - session management. This is what makes AgentCore Runtime special for AI agents."

**[SHOW SESSION SCRIPT]**
```python
# session_example.py
session_id = f"user-demo-conversation-{uuid.uuid4()}"

# Message 1
response1 = client.invoke_agent_runtime(
    agentRuntimeArn=agent_arn,
    runtimeSessionId=session_id,
    payload=json.dumps({"prompt": "My name is Alice, tell me about EC2"})
)

# Message 2 - Same session ID
response2 = client.invoke_agent_runtime(
    agentRuntimeArn=agent_arn,
    runtimeSessionId=session_id,  # Same session!
    payload=json.dumps({"prompt": "What was my name again?"})
)
```

**[RUN THE DEMO]**
"Watch this - I'm going to have a conversation with our agent:"

**[SHOW CONVERSATION]**
- "First message: 'My name is Alice, tell me about EC2'"
- "Second message: 'What was my name again?'"

**[SHOW AGENT REMEMBERING]**
"Look at that! The agent remembered Alice's name and the entire conversation context. This is because AgentCore Runtime provides session isolation - each conversation gets its own dedicated microVM that persists for up to 8 hours."

**[EXPLAIN SESSION BENEFITS]**
- "15-minute idle timeout"
- "8-hour maximum lifetime"
- "Complete isolation between users"
- "Context preserved across invocations"

---

### STREAMING RESPONSES (13:00 - 13:30)

**[TERMINAL]**

"And here's one more powerful feature - streaming responses. Perfect for real-time user experiences."

**[SHOW STREAMING CODE]**
```python
# my_agent_streaming.py
@app.entrypoint
async def agent_invocation(payload):
    user_message = payload.get("prompt", "Hello!")
    stream = agent.stream_async(user_message)
    async for event in stream:
        yield (event)
```

**[QUICK DEPLOY]**
"I can deploy this streaming version just as easily:"

```bash
agentcore configure -e my_agent_streaming.py
agentcore launch
```

**[TEST STREAMING]**
```bash
python invoke_streaming_agent.py "STREAMING_AGENT_ARN" "Tell me a story"
```

**[SHOW STREAMING OUTPUT]**
"Watch this - instead of waiting for the complete response, we get the text as it's being generated. Perfect for chatbots and interactive applications where users want to see responses in real-time."

---

### PRODUCTION FEATURES (13:30 - 14:00)

**[SCREEN: AWS Console]**

"Let's quickly look at what we get in production:"

**[SHOW CLOUDWATCH LOGS]**
"Automatic logging in CloudWatch - every invocation is tracked."

**[SHOW ECR REPOSITORY]**
"Our container image in ECR - automatically built and managed."

**[SHOW IAM ROLES]**
"Security policies created automatically following AWS best practices."

**[HIGHLIGHT KEY BENEFITS]**
- "Auto-scaling based on demand"
- "Built-in security and isolation"
- "Monitoring and observability"
- "No infrastructure to manage"

"This is production-ready infrastructure that would normally take weeks to set up, and we did it in 15 minutes."

---

### WRAP UP & NEXT EPISODE (14:00 - 15:00)

**[SUMMARY SCREEN]**

"Let's recap what we accomplished today:"

**[CHECKLIST ANIMATION]**
✅ "Built an AI agent with 10 lines of code"
✅ "Deployed to production with 2 commands"
✅ "Demonstrated session-aware conversations"
✅ "Got auto-scaling, security, and monitoring for free"

**[CLEANUP NOTE]**
"Oh, and if you want to clean up everything we created today, just run:"

```bash
agentcore destroy
```

"This removes all the AWS resources - the runtime, ECR repository, IAM roles, and CloudWatch logs. Perfect for experimentation without ongoing costs."

**[NEXT EPISODE TEASER]**
"In our next episode, we're diving deep into AgentCore Identity. I'll show you how to securely manage API keys for external models like OpenAI and Anthropic, set up OAuth authentication, and handle credential rotation - all without exposing secrets in your code."

**[CALL TO ACTION]**
"If this saved you weeks of DevOps work, smash that like button and subscribe for the rest of the series. Drop a comment with what AgentCore service you want to see next."

**[FINAL HOOK]**
"Remember - if you can write 10 lines of Python, you can deploy production AI agents. See you in the next episode!"

**[END SCREEN: Subscribe + Next Video Thumbnail]**

---

## TIMING BREAKDOWN:
- Intro & Hook: 1:30
- Problem Setup: 1:30  
- AgentCore Overview: 2:00
- Any Framework/Model: 1:30
- Demo Setup: 1:30
- Local Testing: 1:00
- Deployment: 2:00
- Session Demo: 2:00
- Production Features: 1:00
- Wrap Up: 1:00
**Total: 15:00**

## KEY VISUAL ELEMENTS:
- Code snippets with syntax highlighting
- Terminal demonstrations
- AWS Console screenshots
- Animated service diagrams
- Progress indicators during builds
- Before/after comparisons

## ENGAGEMENT HOOKS:
- "2 commands" promise in first 15 seconds
- Live coding and deployment
- Real conversation demonstration
- Clear problem → solution narrative
- Strong next episode teaser
