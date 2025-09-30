from bedrock_agentcore.tools.browser_client import browser_session
from nova_act import NovaAct, BOOL_SCHEMA, ActAgentError
from rich.console import Console
from rich.panel import Panel
import sys
import json
import time
import argparse
sys.path.append("../interactive_tools")
from browser_viewer import BrowserViewerServer


console = Console()

from boto3.session import Session

boto_session = Session()
region = boto_session.region_name
print("using region", region)

def contains_human_validation_error(err):
    """
    Recursively check if the error or its message attribute indicates HumanValidationError.
    """
    if err is None:
        return False

    # Direct string check
    if isinstance(err, str) and "HumanValidationError" in err:
        return True

    # If err has 'message' attribute that's string or another error, recurse
    if hasattr(err, "message"):
        return contains_human_validation_error(err.message)

    # If err has string representation containing the error text
    if "HumanValidationError" in str(err):
        return True

    return False

def live_view_with_nova_act(steps, starting_page, nova_act_key, region="us-west-2"):
    """Run the browser live viewer with display sizing."""
    console.print(
        Panel(
            "[bold cyan]Browser Live Viewer[/bold cyan]\n\n"
            "This demonstrates:\n"
            "• Live browser viewing with DCV\n"
            "• Configurable display sizes (not limited to 900×800)\n"
            "• Proper display layout callbacks\n\n"
            "[yellow]Note: Requires Amazon DCV SDK files[/yellow]",
            title="Browser Live Viewer",
            border_style="blue",
        )
    )
    result = None

    try:
        # Step 1: Create browser session
        with browser_session(region) as client:
            ws_url, headers = client.generate_ws_headers()

            # Step 2: Start viewer server
            console.print("\n[cyan]Step 3: Starting viewer server...[/cyan]")
            viewer = BrowserViewerServer(client, port=8000)
            viewer_url = viewer.start(open_browser=True)

            # Step 3: Show features
            console.print("\n[bold green]Viewer Features:[/bold green]")
            console.print(
                "• Default display: 1600×900 (configured via displayLayout callback)"
            )
            console.print("• Size options: 720p, 900p, 1080p, 1440p")
            console.print("• Real-time display updates")
            console.print("• Take/Release control functionality")

            console.print("\n[yellow]Press Ctrl+C to stop[/yellow]")

            # Step 4: Use Nova Act to interact with the browser
            with NovaAct(
                cdp_endpoint_url=ws_url,
                cdp_headers=headers,
                preview={"playwright_actuation": True},
                nova_act_api_key=nova_act_key,
                starting_page=starting_page,
            ) as nova_act:

                for step_index, step in enumerate(steps):
                    max_retries = 3
                    retry_count = 0

                    while retry_count < max_retries:
                        try:
                            print(f"Executing step {step_index + 1}/{len(steps)}: {step}")
                            result = nova_act.act(step)
                            console.print(f"\n[bold green]Step {step_index + 1} Result:[/bold green] {result}")
                            break  # Success, move to next step

                        except ActAgentError as err:
                            # Check for human validation in the error message or structure
                            if contains_human_validation_error(err):
                                print("CAPTCHA detected! Please solve it in the browser.")
                                captcha_wait_attempts = 0
                                max_captcha_wait_attempts = 8

                                while captcha_wait_attempts < max_captcha_wait_attempts:
                                    try:
                                        time.sleep(10)  # Give user time to solve captcha
                                        captcha_result = nova_act.act(
                                            "Is there a captcha on the screen?", schema=BOOL_SCHEMA
                                        )

                                        if captcha_result.matches_schema and not captcha_result.parsed_response:
                                            print("Captcha solved, continuing with current step...")
                                            # Don't increment retry_count so we retry the current step without penalty
                                            break
                                        else:
                                            print(f"Captcha still present. Waiting... (Attempt {captcha_wait_attempts + 1}/{max_captcha_wait_attempts})")
                                            captcha_wait_attempts += 1

                                    except Exception as captcha_check_err:
                                        print(f"Error checking captcha status: {str(captcha_check_err)}")
                                        captcha_wait_attempts += 1
                                        time.sleep(5)

                                if captcha_wait_attempts >= max_captcha_wait_attempts:
                                    print("Maximum captcha wait attempts reached. Trying to continue anyway.")
                                    retry_count += 1

                            else:
                                print(f"Non-captcha error occurred: {str(err)}")
                                retry_count += 1
                                time.sleep(5)

                        except Exception as general_err:
                            print(f"Unexpected error on step {step_index + 1}: {str(general_err)}")
                            retry_count += 1
                            time.sleep(5)

                    if retry_count >= max_retries:
                        console.print(f"\n[bold red]Failed to complete step {step_index + 1} after {max_retries} attempts.[/bold red]")
                        if step_index < len(steps) - 1:
                            console.print("[yellow]Attempting to continue with next step...[/yellow]")

                # Final summary
                console.print("\n[bold blue]Task Execution Complete[/bold blue]")

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
    finally:
        console.print("\n\n[yellow]Shutting down...[/yellow]")
        if "client" in locals():
            client.stop()
            console.print("✅ Browser session terminated")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", required=False, help="JSON array or comma-separated list of steps to execute", 
                        default='["Search for AI news and press enter. If there is alredy AI news typed in search bar, then do not do anything", "Get the first AI news result, open the page and extract the title. Instead, if you see an AI summary, extract the first paragrpah of the summary and return"]')
    parser.add_argument("--starting-page", required=True, help="Starting URL")
    parser.add_argument("--nova-act-key", required=True, help="Nova Act API key")
    parser.add_argument("--region", default="us-west-2", help="AWS region")
    args = parser.parse_args()

    # Parse steps - accept either a JSON array or comma-separated values
    try:
        # Try parsing as JSON first
        steps = json.loads(args.steps)
    except json.JSONDecodeError:
        # If not valid JSON, treat as comma-separated string
        steps = [step.strip() for step in args.steps.split(',')]

    # Ensure steps is a list
    if not isinstance(steps, list):
        steps = [steps]

    result = live_view_with_nova_act(
        steps, args.starting_page, args.nova_act_key, args.region
    )
