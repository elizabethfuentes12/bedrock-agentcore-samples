from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from strands import Agent
from uuid import uuid4
import datetime
from strands.session.file_session_manager import FileSessionManager
from botocore.config import Config
from typing import AsyncGenerator, Any

import boto3

from streamable_http_sigv4 import streamablehttp_client_with_sigv4

config = Config(retries={"max_attempts": 10, "mode": "adaptive"})
today = datetime.datetime.today().strftime("%A, %B %d, %Y")


def create_streamable_http_transport_sigv4(
    mcp_url: str, service_name: str, region: str
):
    """
    Create a streamable HTTP transport with AWS SigV4 authentication.

    This function creates an MCP client transport that uses AWS Signature Version 4 (SigV4)
    to authenticate requests. Essential for connecting to IAM-authenticated gateways.

    Args:
        mcp_url (str): The URL of the MCP gateway endpoint
        service_name (str): The AWS service name for SigV4 signing
        region (str): The AWS region where the gateway is deployed

    Returns:
        StreamableHTTPTransportWithSigV4: A transport instance configured for SigV4 auth
    """
    # Get AWS credentials from the current boto3 session
    # These credentials will be used to sign requests with SigV4

    session = boto3.Session()
    credentials = session.get_credentials()

    return streamablehttp_client_with_sigv4(
        url=mcp_url,
        credentials=credentials,  # Uses credentials from the Lambda execution role
        service=service_name,
        region=region,
    )

SYSTEM_PROMPT = """
You are an AWS Expert specializing in deep, comprehensive information gathering, analysis and guidance. Your mission is to conduct comprehensive, accurate, and up-to-date research, grounding your findings in credible web sources.

**Today's Date:** {today}

RULES:
- You must start the research process by creating a plan. Think step by step about what you need to do to answer the research question.
- You can iterate on your research plan and research response multiple times, using combinations of the tools available to you until you are satisfied with the results.
"""


class AgentService:
    def __init__(
        self,
        gatewayURL,
        model_id,
        system_prompt=SYSTEM_PROMPT,
        sesion_id=str(uuid4()),
    ):

        self.gatewayURL = gatewayURL
        self.model_id = model_id
        self.system_prompt = system_prompt
        self.session_id = sesion_id
        self.model = BedrockModel( boto_client_config=config, model_id=self.model_id, max_tokens=4096)
        self.tools = self.get_mcp_tools()

        self.session_manager = FileSessionManager(session_id=self.session_id)

        self.agent = Agent(
            model=self.model,
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
            session_manager=self.session_manager,
        )

    def get_mcp_tools(self):
        self.mcp_client = None
        if self.gatewayURL:

            # Create the MCP client with SigV4 authentication
            self.mcp_client = MCPClient(
                lambda: create_streamable_http_transport_sigv4(
                    mcp_url=self.gatewayURL,  # Gateway URL should be set as an environment variable
                    service_name="bedrock-agentcore",
                    region=boto3._get_default_session().region_name,  # type: ignore
                )
            )

            with self.mcp_client:
                return self.mcp_client.list_tools_sync()
        else:
            return []

    def invoke(self, query):
        if self.mcp_client:
            with self.mcp_client:
                return self.agent(query)
        else:
            return self.agent(query)

    async def invoke_async(self, query) -> AsyncGenerator[Any, None]:

        if self.mcp_client:
            with self.mcp_client:
                agent_stream = self.agent.stream_async(query)
                async for chunk in agent_stream:  # ignore
                    if "agent" in chunk:
                        del chunk["agent"]
                    if "event_loop_cycle_id" in chunk:
                        del chunk["event_loop_cycle_id"]
                    if "event_loop_parent_cycle_id" in chunk:
                        del chunk["event_loop_parent_cycle_id"]
                    if "system_prompt" in chunk:
                        del chunk["system_prompt"]
                    if "model" in chunk:
                        del chunk["model"]
                    if "event_loop_cycle_trace" in chunk:
                        del chunk["event_loop_cycle_trace"]
                    if "event_loop_cycle_span" in chunk:
                        del chunk["event_loop_cycle_span"]
                    if "messages" in chunk:
                        del chunk["messages"]
                    if "tool_config" in chunk:
                        del chunk["tool_config"]

                    if chunk.get("delta", {}).get("toolUse"):
                        continue
                    if chunk.get("contentBlockDelta", {}).get("delta", {}).get("toolUse"):
                        continue
                    if (
                        chunk.get("event", {})
                        .get("contentBlockDelta", {})
                        .get("delta", {})
                        .get("toolUse")
                    ):
                        continue

                    yield chunk

        else:
            agent_stream = self.agent.stream_async(query)
            async for chunk in agent_stream:
                yield chunk
