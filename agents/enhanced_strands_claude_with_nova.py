# Example: Enhanced Strands agent with Nova Act browser tool
from strands import Agent, tool
from strands_tools import calculator
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.tools.browser_client import browser_session
from nova_act import NovaAct
import json

app = BedrockAgentCoreApp()

# Original custom tool 
@tool
def weather():
    """ Get weather """ 
    return "sunny"

# NEW: Nova Act browser tool
@tool
def browse_web(instruction: str, starting_url: str = "https://google.com"):
    """Use Nova Act to browse the web and complete web-based tasks

    Args:
        instruction: What you want to accomplish on the web
        starting_url: URL to start from

    Returns:
        Result of the web browsing task
    """
    try:
        with browser_session("us-east-1") as browser_client:
            ws_url, headers = browser_client.generate_ws_headers()

            with NovaAct(
                cdp_endpoint_url=ws_url,
                cdp_headers=headers,
                nova_act_api_key="your-nova-act-api-key",  # Replace with your key
                starting_page=starting_url,
            ) as nova_act:
                result = nova_act.act(instruction)
                return f"Web task completed: {str(result)}"
    except Exception as e:
        return f"Error browsing web: {str(e)}"

# Initialize enhanced agent with Nova Act
model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
model = BedrockModel(model_id=model_id)

agent = Agent(
    model=model,
    tools=[calculator, weather, browse_web],  # Now includes web browsing!
    system_prompt="You're a helpful assistant. You can do math calculations, tell the weather, and browse the web to find information."
)

@app.entrypoint
def enhanced_strands_agent(payload):
    """Enhanced agent that can browse the web"""
    user_input = payload.get("prompt")
    print("User input:", user_input)
    response = agent(user_input)
    return response.message['content'][0]['text']

if __name__ == "__main__":
    app.run()
