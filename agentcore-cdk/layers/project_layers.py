import json
from constructs import Construct

from aws_cdk import (
    aws_lambda as _lambda
)



class Bs4Requests(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.layer = _lambda.LayerVersion(
            self, "Requests", code=_lambda.Code.from_asset("./layers/bs4requests.zip"),
            compatible_runtimes = [_lambda.Runtime.PYTHON_3_12, _lambda.Runtime.PYTHON_3_13], 
            description = 'Requests')

