from aws_cdk import (
    aws_iam as iam,
    Stack,
    aws_bedrockagentcore as bedrockagentcore,
)
from constructs import Construct


class AgentCoreGateway(Construct):

    def __init__(
        self, scope: Construct, construct_id: str, name, description, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.create_gateway(name, description)

    def create_gateway(self, name, description=""):
        self.create_role()

        self.gateway = bedrockagentcore.CfnGateway(
            self,
            "Gateway",
            authorizer_type="AWS_IAM",
            name=name,
            protocol_type="MCP",
            role_arn=self.role.role_arn,
            description=description,
        )
        

        self.gateway.node.add_dependency(self.role)

    def add_lambda_target(self, target_name, description, input_schema, lambda_arn):


        payload = {
            "name": target_name,
            "description": description,
            "inputSchema": input_schema,
        }

        target = bedrockagentcore.CfnGatewayTarget(
            self,
            f"Target-{target_name}",
            name=target_name.replace("_","-") + "-target",
            gateway_identifier=self.gateway.attr_gateway_identifier,
            credential_provider_configurations=[
                bedrockagentcore.CfnGatewayTarget.CredentialProviderConfigurationProperty(
                    credential_provider_type="GATEWAY_IAM_ROLE"
                )
            ],
            target_configuration=bedrockagentcore.CfnGatewayTarget.TargetConfigurationProperty(
                mcp=bedrockagentcore.CfnGatewayTarget.McpTargetConfigurationProperty(
                    lambda_=bedrockagentcore.CfnGatewayTarget.McpLambdaTargetConfigurationProperty(
                        lambda_arn=lambda_arn,
                        tool_schema=bedrockagentcore.CfnGatewayTarget.ToolSchemaProperty(
                            inline_payload=[payload]
                        ),
                    )
                )
            ),
            description=description[:200],
        )
        target.node.add_dependency(self.gateway)
        return target

    def create_role(self):
        stk = Stack.of(self)
        region = stk.region
        account_id = stk.account

        self.role = iam.Role(
            self,
            "BedrockGatewayRole",
            assumed_by=iam.ServicePrincipal(
                service="bedrock-agentcore.amazonaws.com",
                conditions={
                    "StringEquals": {"aws:SourceAccount": account_id},
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock-agentcore:{region}:{account_id}:*"
                    },
                },
            ),  # type: ignore
        )
        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock-agentcore:*",
                    "bedrock:*",
                    "agent-credential-provider:*",
                    "iam:PassRole",
                    "secretsmanager:GetSecretValue",
                    "lambda:InvokeFunction",
                ],
                resources=["*"],
            )
        )
