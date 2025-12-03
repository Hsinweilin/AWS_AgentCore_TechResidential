import os
import sys
import boto3
from strands import Agent, tool
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import tempfile
from datetime import datetime
from rich.console import Console
import time
import glob
import shutil
import ast
import json

app = BedrockAgentCoreApp()

# Set AWS region
REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Create an SSM client
ssm = boto3.client('ssm', region_name=REGION)
response = ssm.get_parameter(
    Name="NOVA_ACT_API_KEY",
    WithDecryption=True
)
nova_act_api_key = response['Parameter']['Value']
print(f"✅ Nova Act API Key retrieved")

# tool to perform web automation and download files using Nova Act
@tool
def nova_act_download(instruction: str, starting_url: str, client_name: str):
    """Download files from websites using Nova Act automation
    
    Args:
        instruction: The task to perform (including login and actions)
        starting_url: The website URL to start automation
        client_name: Client identifier for S3 organization
    
    Returns:
        dict: Status and file information or error details
    """
    # Import inside function to avoid pydantic conflicts
    try:
        from nova_act import NovaAct
    except Exception as import_error:
        return {"status": "error", "reason": f"Failed to import NovaAct: {str(import_error)}"}

    console = Console()
    download_dir = tempfile.gettempdir()
    file_path = None
    download_triggered = False

    try:
        with NovaAct(
            headless=True,
            nova_act_api_key=nova_act_api_key,
            starting_page=starting_url
        ) as nova_act:
            
            prompt = """You are a helpful Web UI automation assistant.
SYSTEM PROMPT:
- Even the task cannot be completed, always return ACTION COMPLETE, never return error !!!!!
- YOU SHOULD NEVER REPEAT THE SAME ACTION MORE THAN ONCE. If your action is unsuccessful, return ACTION COMPLETE !!!!!
- After clicked on download, even if the page looks like it does not change, immediately return ACTION COMPLETE !!!!!
- YOU SHOULD NEVER DISPLAY the password in plan task during execution. 

USER PROMPT: 

""" + instruction
            
            console.print("[cyan]Starting NovaAct automation...[/cyan]")
            result = nova_act.act(prompt)
            console.print(result)
                
            # Check file system for recent downloads
            possible_download_dirs = []
            temp_base = tempfile.gettempdir()
            playwright_dirs = glob.glob(os.path.join(temp_base, "playwright-*"))
            
            for temp_dir in playwright_dirs:
                downloads_subdir = os.path.join(temp_dir, "downloads")
                if os.path.exists(downloads_subdir):
                    possible_download_dirs.append(downloads_subdir)
                    console.print(f"[cyan]Found Playwright downloads dir: {downloads_subdir}[/cyan]")
            
            for temp_dir in playwright_dirs:
                if os.path.exists(temp_dir):
                    possible_download_dirs.append(temp_dir)
            
            possible_download_dirs.append(download_dir)
            
            current_time = time.time()
            recent_files = []
            
            for location in possible_download_dirs:
                if os.path.exists(location):
                    all_files = glob.glob(os.path.join(location, "*"))
                    for f in all_files:
                        if os.path.isfile(f):
                            file_age = current_time - os.path.getmtime(f)
                            if file_age < 45:
                                recent_files.append((f, os.path.getmtime(f)))
                                console.print(f"[cyan]  ✓ Found recent file ({file_age:.1f}s old): {os.path.basename(f)}[/cyan]")
            
            if recent_files:
                recent_files.sort(key=lambda x: x[1], reverse=True)
                most_recent_file = recent_files[0][0]
                console.print(f"[green]✅ Found downloaded file: {most_recent_file}[/green]")
                
                file_path = os.path.join(download_dir, os.path.basename(most_recent_file))
                shutil.copy2(most_recent_file, file_path)
                download_triggered = True
                console.print(f"Copied to: {file_path}")
            else:
                console.print("[red]No recent files found in download directories[/red]")
            
            if not file_path:
                console.print("[yellow]No download detected, trying expect_download...[/yellow]")
                try:
                    with nova_act.page.expect_download(timeout=5000) as download_info:
                        result = nova_act.act("Click the download button once and IMMEDIATELY RETURN ACTION COMPLETE")
                    
                    if download_info.value:
                        console.print("[green]✅ Download event captured[/green]")
                        original_filename = download_info.value.suggested_filename
                        if callable(original_filename):
                            original_filename = original_filename() or "downloaded_file"
                        
                        file_path = os.path.join(download_dir, original_filename)
                        download_info.value.save_as(file_path)
                        console.print(f"Downloaded via event: {file_path}")
                except TimeoutError:
                    console.print("[yellow]No download event detected[/yellow]")
                except Exception as e:
                    console.print(f"[yellow]Download event check failed: {e}[/yellow]")
            
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                file_ext = os.path.splitext(file_path)[1]
                
                if file_size == 0:
                    console.print("[red]Downloaded file is empty[/red]")
                    return {"status": "error", "reason": "File is empty"}
                
                if file_ext == '.crdownload' or file_ext == '.part':
                    console.print("[red]File is still downloading (partial file detected)[/red]")
                    return {"status": "error", "reason": "Partial download detected"}
                
                console.print(f"[green]File size: {file_size} bytes, Extension: {file_ext}[/green]")
                
                s3 = boto3.client('s3', region_name=REGION)
                bucket_name = "bedrock-web-automation-dev-storage"
                s3_file_key = f"downloaded-files/{client_name}/{os.path.basename(file_path)}"
                
                try:
                    s3.upload_file(file_path, bucket_name, s3_file_key)
                    presigned_url = s3.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': bucket_name, 'Key': s3_file_key},
                        ExpiresIn=3600
                    )
                    console.print(f"✅ Uploaded to S3: {s3_file_key}")
                    return {
                        "status": "success",
                        "s3_key": s3_file_key,
                        "s3_url": presigned_url,
                        "file_name": os.path.basename(file_path),
                        "file_size": file_size,
                        "method": "filesystem_check" if download_triggered else "event"
                    }
                except Exception as s3_error:
                    console.print(f"❌ Error uploading to S3: {repr(s3_error)}")
                    return {"status": "s3_error", "reason": repr(s3_error)}
            else:
                return {"status": "error", "reason": "File not downloaded - all methods failed"}
                
    except Exception as e:
        console.print(f"[red]❌ Error in nova_act_download: {repr(e)}[/red]")
        return {"status": "error", "reason": f"NovaAct execution failed: {repr(e)}"}


model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
model = BedrockModel(model_id=model_id)
agent = Agent(
    model=model,
    tools=[nova_act_download],
    system_prompt="""You are a helpful Web UI automation assistant.

IMPORTANT BEHAVIOR RULES:
- Do NOT retry failed tool calls on your own. If a tool fails, explain the error and stop.
- Never output the password in plain text in your responses.
- Never make multiple attempts to run the same web automation in a single response.

IMPORTANT:
After running a tool, you MUST produce a final assistant message containing ONLY the JSON returned by the tool.

You will receive structured data with these fields:
- Target Website URL, Login Username, Login Password, Task Instructions, Client Name

Follow this exact process:
1. Extract the website URL, login credentials, and task instructions
2. Use the nova_act_download tool with THREE arguments:
   a. instruction: "Login using username: {username} and password: {password}. Then {task instructions}."
   b. starting_url: The website URL
   c. client_name: The client identifier
3. IMPORTANT: Return ONLY the JSON response from the tool, do not add any additional text or summary.
   Return the exact dict that the tool returns with these fields: status, s3_key, s3_url, file_name, file_size, method
"""
)

@app.entrypoint
def invoke_agent(payload):
    """Process JSON payload and return structured result"""
    
    weburl = payload.get("weburl")
    username = payload.get("username")
    password = payload.get("password")
    promptfile = payload.get("promptfile")
    client_name = payload.get("client_name")
    
    if not all([weburl, username, password, promptfile, client_name]):
        return {"status": "error", "message": "Missing required fields"}
    
    prompt = f"""Execute web automation with these details:
- Website URL: {weburl}
- Username: {username}
- Password: {password}
- Task: {promptfile}
- Client: {client_name}
"""
    
    print("🚀 Invoking agent with Claude...")
    response = agent(prompt)
    # Debug: print the structure
    content = response.message["content"]
    print(f"✅ Agent response received")
    print(f"Response type: {type(content)}")
    print(f"Response content: {content}")
        
    # content is a LIST: [{'text': '{"status": "success", ...}'}]
    raw = content[0]["text"]
    print(f"Raw text: {raw}")
        
    # The text is JSON (double quotes), use json.loads
    try:
        result = json.loads(raw)
        print(f"✅ Parsed with json.loads: {result}")
    except json.JSONDecodeError:
        # Fallback to ast.literal_eval for Python dict format
        try:
            result = ast.literal_eval(raw)
            print(f"✅ Parsed with ast.literal_eval: {result}")
        except (ValueError, SyntaxError) as e:
            print(f"❌ Both parsers failed: {e}")
            return {"status": "error", "message": "Failed to parse response", "raw": raw[:200]}
        
    # Ensure we return a dict
    if isinstance(result, dict):
        return result
    else:
        return {"status": "error", "message": f"Unexpected type: {type(result).__name__}"}

    
if __name__ == "__main__":
    app.run()