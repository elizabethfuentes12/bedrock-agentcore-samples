import boto3
import json
import time
import uuid
import getpass
import logging  

def deploy_infrastructure():
    """Deploy CloudFormation stack for customer support infrastructure"""
    cf_client = boto3.client('cloudformation',region_name="us-west-2")
    
    stack_name = "customer-support-lambda-stack"
    template_file = "cloudformation/customer_support_lambda.yaml"
    
    with open(template_file, 'r') as f:
        template_body = f.read()
    
    try:
        cf_client.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Capabilities=['CAPABILITY_IAM']
        )
        
        print(f"Creating stack {stack_name}...")
        waiter = cf_client.get_waiter('stack_create_complete')
        waiter.wait(StackName=stack_name)
        print("Stack created successfully!")
        
    except Exception as e:
        if "AlreadyExistsException" in str(e):
            print("Stack already exists, continuing...")
        else:
            print(f"Error deploying stack: {e}")
            return None, None
    
    # Get outputs
    response = cf_client.describe_stacks(StackName=stack_name)
    outputs = response['Stacks'][0]['Outputs']
    
    lambda_arn = next(o['OutputValue'] for o in outputs if o['OutputKey'] == 'CustomerSupportLambdaArn')
    gateway_role_arn = next(o['OutputValue'] for o in outputs if o['OutputKey'] == 'GatewayAgentCoreRoleArn')
    runtime_role_arn = next(o['OutputValue'] for o in outputs if o['OutputKey'] == 'AgentCoreRuntimeExecutionRoleArn')
    
    return lambda_arn, gateway_role_arn, runtime_role_arn

def create_nasa_credentials():
    """Create NASA API credential provider"""
    identity_client = boto3.client('bedrock-agentcore-control', region_name="us-west-2")
    
    # Get NASA API key from user
    nasa_api_key = getpass.getpass(prompt='Enter your NASA API Key (get it free at https://api.nasa.gov/): ')
    
    if not nasa_api_key:
        print("NASA API Key is required for Mars weather functionality")
        return None
    
    try:
        response = identity_client.create_api_key_credential_provider(
            name="NasaInsightAPIKey",
            apiKey=nasa_api_key,
        )
        return response['credentialProviderArn']
    except Exception as e:
        print(f"Error creating NASA credential provider: {e}")
        return None

def create_gateway(lambda_arn, gateway_role_arn, runtime_role_arn):
    """Create AgentCore Gateway with Lambda and NASA API targets"""
    agentcore_client = boto3.client('bedrock-agentcore-control',region_name="us-west-2")
    identity_client = boto3.client('bedrock-agentcore-control',region_name="us-west-2")
    
    gateway_name = "customer-support-gateway"
    lambda_target_name = "CustomerSupportLambda"
    nasa_target_name = "NasaMarsWeather"
    
    # Check if gateway already exists
    try:
        gateways = agentcore_client.list_gateways()
        existing_gateway = None
        for gateway in gateways['items']:
            if gateway['name'] == gateway_name:
                existing_gateway = gateway
                break
        
        if existing_gateway:
            gateway_id = existing_gateway['gatewayId']
            gateway_details = agentcore_client.get_gateway(gatewayIdentifier=gateway_id)
            gateway_url = gateway_details['gatewayUrl']
            print(f"Using existing gateway: {gateway_id}")
        else:
            # Create gateway with AWS_IAM authorizer
            gateway_response = agentcore_client.create_gateway(
                name=gateway_name,
                roleArn=gateway_role_arn,
                protocolType="MCP",
                authorizerType="AWS_IAM",
                description="Customer Support Gateway with Lambda and NASA API targets"
            )
            
            gateway_id = gateway_response['gatewayId']
            gateway_url = gateway_response['gatewayUrl']
            
            print(f"Gateway created: {gateway_id}")
            
            # Wait for gateway to be ready
            print("Waiting for gateway to be ready...")
            while True:
                status_response = agentcore_client.get_gateway(gatewayIdentifier=gateway_id)
                status = status_response['status']
                if status in ['READY', 'ACTIVE']:
                    print(f"Gateway is now {status.lower()}!")
                    break
                elif status == 'FAILED':
                    raise Exception("Gateway creation failed")
                time.sleep(5)
    
    except Exception as e:
        print(f"Error with gateway: {e}")
        return None
    
    # Create Lambda target
    try:
        targets = agentcore_client.list_gateway_targets(gatewayIdentifier=gateway_id)
        lambda_exists = any(t['name'] == lambda_target_name for t in targets['items'])
        
        if not lambda_exists:
            lambda_target_config = {
                "mcp": {
                    "lambda": {
                        "lambdaArn": lambda_arn, 
                        "toolSchema": {
                            "inlinePayload": [
                                {
                                    "name": "get_customer_profile",
                                    "description": "Retrieve customer profile using customer ID, email, or phone number",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "customer_id": {"type": "string"},
                                            "email": {"type": "string"},
                                            "phone": {"type": "string"},
                                        },
                                        "required": ["customer_id"],
                                    },
                                },
                                {
                                    "name": "check_warranty_status",
                                    "description": "Check the warranty status of a product using its serial number and optionally verify via email",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "serial_number": {"type": "string"},
                                            "customer_email": {"type": "string"},
                                        },
                                        "required": ["serial_number"],
                                    },
                                },
                            ]
                        },
                    }
                }
            }
            
            credential_config = [{"credentialProviderType": "GATEWAY_IAM_ROLE"}]
            
            agentcore_client.create_gateway_target(
                gatewayIdentifier=gateway_id,
                name=lambda_target_name,
                description="Lambda Target for Customer Support",
                targetConfiguration=lambda_target_config,
                credentialProviderConfigurations=credential_config
            )
            print("Lambda target created successfully!")
    
    except Exception as e:
        print(f"Error with Lambda target: {e}")
    
    # Create NASA API target
    try:
        nasa_exists = any(t['name'] == nasa_target_name for t in targets['items'])
        
        if not nasa_exists:
            print("Setting up NASA API target...")
            
            # Check if credential provider exists
            credential_provider_arn = None
            try:
                providers = identity_client.list_api_key_credential_providers()
                for provider in providers['credentialProviders']:
                    if provider['name'] == "NasaInsightAPIKey":
                        credential_provider_arn = provider['credentialProviderArn']
                        print("Using existing NASA credential provider")
                        break
            except:
                pass
            
            # Create credential provider if doesn't exist
            if not credential_provider_arn:
                nasa_api_key = getpass.getpass(prompt='Enter your NASA API Key (get free at https://api.nasa.gov/): ')
                if not nasa_api_key:
                    print("Skipping NASA target - no API key provided")
                    return gateway_url
                
                response = identity_client.create_api_key_credential_provider(
                    name="NasaInsightAPIKey",
                    apiKey=nasa_api_key,
                )
                credential_provider_arn = response['credentialProviderArn']
                print("Created NASA credential provider")

            # Create S3 bucket and upload OpenAPI spec
            session = boto3.Session()
            region = session.region_name or 'us-east-1'
            s3_client = session.client('s3')
            
            unique_s3_name = str(uuid.uuid4())
            bucket_name = f'agentcore-gateway-{unique_s3_name}'
            file_path = 'openapi-specs/nasa_mars_insights_openapi.json'
            object_key = 'nasa_mars_insights_openapi.json'

            if region == "us-east-1":
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            
            with open(file_path, 'rb') as file_data:
                s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=file_data)

            openapi_s3_uri = f's3://{bucket_name}/{object_key}'
            print('Uploaded OpenAPI spec to S3')

            # Configure and create NASA target
            nasa_target_config = {
                "mcp": {
                    "openApiSchema": {
                        "s3": {"uri": openapi_s3_uri}
                    }
                }
            }

            api_key_credential_config = [{
                "credentialProviderType": "API_KEY",
                "credentialProvider": {
                    "apiKeyCredentialProvider": {
                        "credentialParameterName": "api_key",
                        "providerArn": credential_provider_arn,
                        "credentialLocation": "QUERY_PARAMETER"
                    }
                }
            }]

            agentcore_client.create_gateway_target(
                gatewayIdentifier=gateway_id,
                name=nasa_target_name,
                description='NASA Mars Weather API Target',
                targetConfiguration=nasa_target_config,
                credentialProviderConfigurations=api_key_credential_config
            )
            print("NASA target created successfully!")
    
    except Exception as e:
        print(f"Error with NASA target setup: {e}")
    
    return gateway_url

def main():
    print("=== Setting up Customer Support Gateway ===\n")
    
    # Get current region and stack name
    session = boto3.Session()
    region = session.region_name or 'us-east-1'
    stack_name = "customer-support-lambda-stack"
    
    # Step 1: Deploy infrastructure
    print("1. Deploying infrastructure...")
    lambda_arn, gateway_role_arn, runtime_role_arn = deploy_infrastructure()
    
    if not lambda_arn:
        print("Failed to deploy infrastructure")
        return
    
    # Step 2: Create gateway
    print("\n2. Creating AgentCore Gateway...")
    gateway_url = create_gateway(lambda_arn, gateway_role_arn, runtime_role_arn)
    
    if gateway_url:
        print(f"\n=== Setup Complete ===")
        print(f"Region: {region}")
        print(f"Stack Name: {stack_name}")
        print(f"Gateway URL: {gateway_url}")
        print(f"🔐 Execution Role ARN: {runtime_role_arn}")
        print(f"\n📋 Next Steps:")
        print(f"1. Copy the Execution Role ARN above for 'bedrock-agentcore configure'")
        print(f"2. Use Gateway URL as GATEWAY_URL environment variable for 'bedrock-agentcore launch'")
    else:
        print("Failed to create gateway")

if __name__ == "__main__":
    main()
