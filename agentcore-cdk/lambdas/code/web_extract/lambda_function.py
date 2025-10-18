from web_extract import web_extract


def lambda_handler(event: dict, context) -> dict:
    # event: The event schema should match whatever inputSchema you define for the target.
    # context: Sample event
    # ClientContext([custom={'bedrockAgentCoreGatewayId': 'Y02ERAYBHB', 'bedrockAgentCoreTargetId': 'RQHDN3J002', 'bedrockAgentCoreMessageVersion': '1.0', 'bedrockAgentCoreToolName': 'weather_tool', 'bedrockAgentCoreSessionId': ''},env=None,client=None])
    toolName = context.client_context.custom['bedrockAgentCoreToolName']
    print(context.client_context)
    print(event)
    print(f"Original toolName: , {toolName}")
    delimiter = "___"
    if delimiter in toolName:
        toolName = toolName[toolName.index(delimiter) + len(delimiter):]
    print(f"Converted toolName: , {toolName}")

    results = "no such tool"

    if toolName == 'web_extract':
        results = web_extract( **event)
    else:
        print ("Results:")

    print(results)
    return {'statusCode': 200, 'body': results}
