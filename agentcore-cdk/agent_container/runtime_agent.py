from bedrock_agentcore.runtime import BedrockAgentCoreApp # type: ignore
import logging
import os
from agent_class import AgentService


app = BedrockAgentCoreApp()
app.logger.setLevel(logging.ERROR)

GATEWAY_URL = os.environ.get("GATEWAY_URL")
MODEL_ID = os.environ.get("MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0")


SYSTEM_PROMPT = """
You are an AWS Expert specializing in deep, comprehensive information gathering, analysis and guidance. Your mission is to conduct comprehensive, accurate, and up-to-date research, grounding your findings in credible web sources.

**Today's Date:** {today}

RULES:
- You must start the research process by creating a plan. Think step by step about what you need to do to answer the research question.
- You can iterate on your research plan and research response multiple times, using combinations of the tools available to you until you are satisfied with the results.
"""


@app.entrypoint
async def strands_agent_bedrock_streaming(payload, context):
    """
    Invoke the agent with streaming capabilities
    This function demonstrates how to implement streaming responses
    with AgentCore Runtime using async generators
    """
    print("payload", payload)
    user_input = payload.get("prompt")

    print("User input:", user_input)
    print("Session ID:", context.session_id)
    print("Gateway URL:", GATEWAY_URL)
    print("Model ID:", MODEL_ID)


    print("Initializing Agent Now:")
    agent = AgentService( gatewayURL=GATEWAY_URL, model_id=MODEL_ID, sesion_id=context.session_id)


    print("Invoking Agent Now:")

    try:
        agent_stream = agent.invoke_async([{"text": user_input}])
        async for chunk in agent_stream:  # ignore
            yield chunk

    except Exception as e:
        # Handle errors gracefully in streaming context
        error_response = {"error": str(e), "type": "stream_error"}
        print(f"Streaming error: {error_response}")
        yield error_response

if __name__ == "__main__":
    app.run()
