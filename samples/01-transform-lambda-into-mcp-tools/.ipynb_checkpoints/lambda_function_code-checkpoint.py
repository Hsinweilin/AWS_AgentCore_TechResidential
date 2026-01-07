
# This Lambda function is designed to be used as an MCP tool in Bedrock AgentCore Gateway.
# It routes requests based on the tool name provided in the invocation context.
import json


def lambda_handler(event, context):
    # event: The input payload sent to the Lambda function. Should match the inputSchema defined for the MCP tool.
    # context: Lambda context object, includes custom fields set by AgentCore Gateway.
    # Example context.client_context.custom:
    #   {
    #     'bedrockAgentCoreGatewayId': '...',
    #     'bedrockAgentCoreTargetId': '...',
    #     'bedrockAgentCoreMessageVersion': '1.0',
    #     'bedrockAgentCoreToolName': 'weather_tool',
    #     'bedrockAgentCoreSessionId': ''
    #   }

    # Extract the tool name from the custom context field
    toolName = context.client_context.custom['bedrockAgentCoreToolName']
    print("Lambda invocation context:", context.client_context)
    print("Event payload:", event)
    print(f"Original toolName: {toolName}")

    # If the tool name contains a delimiter (___), extract the actual tool name
    delimiter = "___"
    if delimiter in toolName:
        toolName = toolName[toolName.index(delimiter) + len(delimiter):]
    print(f"Converted toolName: {toolName}")

    # Route logic based on tool name
    if toolName == 'get_order_tool':
        # Respond with order status for get_order_tool
        return {'statusCode': 200, 'body': "Order Id 123 is in shipped status"}
    else:
        # Respond with update confirmation for other tools (e.g., update_order_tool)
        return {'statusCode': 200, 'body': "Updated the order details successfully"}
