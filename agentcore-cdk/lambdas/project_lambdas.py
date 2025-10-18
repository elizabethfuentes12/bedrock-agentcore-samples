from aws_cdk import (
    Duration,
    aws_lambda,
)

from constructs import Construct
from layers import Bs4Requests

LAMBDA_TIMEOUT = 900

BASE_LAMBDA_CONFIG = dict(
    timeout=Duration.seconds(LAMBDA_TIMEOUT),
    memory_size=512,
    runtime=aws_lambda.Runtime.PYTHON_3_13,
    architecture=aws_lambda.Architecture.ARM_64,
    tracing=aws_lambda.Tracing.ACTIVE,
)


class Lambdas(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bs4requests_layer = Bs4Requests(self, "Bs4RequestsLayer")

        # ======================================================================
        # aws_blogs_search tool
        # ======================================================================
        self.aws_blog_search = aws_lambda.Function(
            self,
            "AWSBlogs",
            code=aws_lambda.Code.from_asset("./lambdas/code/aws_blog_search/"),
            layers=[bs4requests_layer.layer],
            handler="lambda_function.lambda_handler",
            **BASE_LAMBDA_CONFIG,  # type: ignore
        )


        # ======================================================================
        # web_extract_tool
        # ======================================================================
        self.web_extract_tool = aws_lambda.Function(
            self,
            "WebExtract",
            code=aws_lambda.Code.from_asset("./lambdas/code/web_extract/"),
            layers=[bs4requests_layer.layer],
            handler="lambda_function.lambda_handler",
            **BASE_LAMBDA_CONFIG,  # type: ignore
        )
