from aws_cdk import (
    CfnOutput,
    Stack,
)
from lambdas import Lambdas

from constructs import Construct
from agent_core_constructs import AgentCoreGateway, AgentCoreRuntime
from target_definitions import aws_blogs_search_target, extract_target

MODEL_ID = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
AGENTCORE_GATEWAY_NAME = "aws-blogs-mcp"
GATEWAY_DESCRIPTION = "AWS Blogs search and page extraction"

AGENT_RUNTIME_NAME = "AWS_Researcher"
AGENT_RUNTIME_DESCRIPTION = "Your AWS Resesarcher using curated Blogs published by AWS Experts"
AGENT_DIRECTORY = "./agent_container"


class AgentcoreCdkStack(Stack):


    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.lambda_functions = Lambdas(self, "L")

        self.agent_core_gateway = AgentCoreGateway( self, "ACG", AGENTCORE_GATEWAY_NAME, GATEWAY_DESCRIPTION)

        self.agent_core_gateway.add_lambda_target(
            extract_target.get("name"),
            extract_target.get("description"),
            extract_target.get("input_schema"),
            self.lambda_functions.web_extract_tool.function_arn,
        )

        self.agent_core_gateway.add_lambda_target(
            aws_blogs_search_target.get("name"),
            aws_blogs_search_target.get("description"),
            aws_blogs_search_target.get("input_schema"),
            self.lambda_functions.aws_blog_search.function_arn,
        )

        self.agent_core_runtime = AgentCoreRuntime(self, "AgentCore")

        env_vars=dict(
            GATEWAY_URL=self.agent_core_gateway.gateway.attr_gateway_url,
            MODEL_ID=MODEL_ID)
        
        self.agent_core_runtime.create_runtime(AGENT_RUNTIME_NAME, AGENT_RUNTIME_DESCRIPTION, AGENT_DIRECTORY, env_vars)
        

        CfnOutput(self, "AgentArn", value=self.agent_core_runtime.runtime.attr_agent_runtime_arn)