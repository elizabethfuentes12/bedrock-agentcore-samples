from aws_cdk import (
    aws_iam as iam,
    Stack,
    aws_bedrockagentcore as bedrockagentcore,
    aws_ecr_assets as ecr_assets,
)
from constructs import Construct

class AgentCoreRuntime(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


    def create_runtime(self,name, description, directory, environment_variables):
        self.create_role()

        self.create_container(directory)

        self.runtime = bedrockagentcore.CfnRuntime(
            self,
            "Runtime",
            agent_runtime_artifact=bedrockagentcore.CfnRuntime.AgentRuntimeArtifactProperty(
                container_configuration=bedrockagentcore.CfnRuntime.ContainerConfigurationProperty(
                    container_uri=self.container_uri
                )
            ),
            agent_runtime_name=name,
            description=description,
            environment_variables=environment_variables,
            network_configuration=bedrockagentcore.CfnRuntime.NetworkConfigurationProperty(
                network_mode="PUBLIC"
            ),
            role_arn=self.role.role_arn,
        )

        self.runtime.node.add_dependency(self.role)
        self.runtime.node.add_dependency(self.image_asset)

    def create_container(self, directory):

        self.image_asset = ecr_assets.DockerImageAsset(
            self,
            "AgentCoreImage",
            directory=directory
        )
        self.container_uri = self.image_asset.image_uri

    def create_role(self):

        stk = Stack.of(self)
        region = stk.region
        account_id = stk.account

        # Create the bedrock agent role
        self.role = iam.Role(
            self,
            "BedrockAgentRole",
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
                    "ecr:*",
                    "dynamodb:*",
                    "cloudwatch:*",
                    "logs:*",
                    "xray:*"
                ],
                resources=["*"],
            )
        )
