# client_http.py

import requests
import json
from rich.console import Console
from rich.syntax import Syntax

console = Console()

def main():
    """
    Client that uses the HTTP /execute endpoint for command execution.
    """
    container_id = input("Enter the container ID: ")
    base_uri = f"http://127.0.0.1:8000/sandboxes/{container_id}"

    console.print(f"[bold green]Connected to sandbox {container_id}. Type 'exit' or press Ctrl+C to quit.[/bold green]")

    while True:
        try:
            command_to_run = console.input("[bold yellow]> [/bold yellow]")

            if command_to_run.lower() == 'exit':
                break

            # Prepare the request payload
            payload = {"command": command_to_run}
            
            # Send the request to the /execute endpoint
            try:
                response = requests.post(f"{base_uri}/execute", json=payload)
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

                # Parse the JSON response
                data = response.json()
                output = data.get("output", "[No output]")
                exit_code = data.get("exit_code", "N/A")

                # Print the output with syntax highlighting
                console.print(f"[dim]Exit Code: {exit_code}[/dim]")
                # Use rich's Syntax for better formatting of shell output
                syntax = Syntax(output, "bash", theme="monokai", line_numbers=False)
                console.print(syntax)

            except requests.exceptions.HTTPError as http_err:
                console.print(f"[bold red]HTTP error occurred: {http_err}[/bold red]")
                if response.text:
                    console.print(f"[red]Response: {response.text}[/red]")
            except requests.exceptions.RequestException as req_err:
                console.print(f"[bold red]Request error occurred: {req_err}[/bold red]")


        except (KeyboardInterrupt, EOFError):
            break
    
    console.print("\n[bold yellow]Exiting client.[/bold yellow]")


if __name__ == "__main__":
    print("This is an HTTP-based client for executing commands.")
    print("Please ensure you have installed the necessary libraries: pip install requests rich")
    main()
