from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
#------------------------------------------------
from bedrock_agentcore.runtime import BedrockAgentCoreApp
app = BedrockAgentCoreApp()
#------------------------------------------------

llm = init_chat_model(
    "us.anthropic.claude-3-5-haiku-20241022-v1:0",
    model_provider="bedrock_converse",
)

# Create graph
graph_builder = StateGraph(State)
...
# Add nodes and edges
...
graph = graph_builder.compile()

# Finally write your entrypoint
@app.entrypoint
def agent_invocation(payload, context):
    
    print("received payload")
    print(payload)
    
    tmp_msg = {"messages": [{"role": "user", "content": payload.get("prompt", "No prompt found in input, please guide customer as to what tools can be used")}]}
    tmp_output = graph.invoke(tmp_msg)
    print(tmp_output)

    return {"result": tmp_output['messages'][-1].content}

app.run()