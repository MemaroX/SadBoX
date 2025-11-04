# client_interactive.py

import asyncio
import websockets
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from rich.console import Console
from rich.text import Text

console = Console()

async def read_from_websocket(websocket):
    """Coroutine to continuously read from the websocket and print to console."""
    try:
        async for message in websocket:
            # Print server output in a different color
            console.print(Text(message, style="cyan"), end="")
    except websockets.exceptions.ConnectionClosed:
        console.print("[bold red]Connection to server closed.[/bold red]")

async def main():
    """Main function to set up connection and handle user input."""
    container_id = input("Enter the container ID: ")
    uri = f"ws://127.0.0.1:8000/sandboxes/{container_id}/ws"

    try:
        async with websockets.connect(uri) as websocket:
            console.print("[bold green]Connected to sandbox. Type 'exit' or press Ctrl+D to quit.[/bold green]")
            
            # Start the task to listen for messages from the server
            read_task = asyncio.create_task(read_from_websocket(websocket))

            session = PromptSession(history=None) # Disable history for now to avoid writing to a file

            # Use patch_stdout to make prompt_toolkit work with other things printing to stdout
            with patch_stdout():
                while True:
                    try:
                        # Get user input asynchronously
                        command = await session.prompt_async("> ")
                        if command.lower() == 'exit':
                            break
                        
                        # Send command to the server
                        await websocket.send(command + "\n")

                    except (EOFError, KeyboardInterrupt):
                        # Ctrl+D or Ctrl+C
                        break
            
            # Clean up
            read_task.cancel()
            console.print("\n[bold yellow]Disconnecting...[/bold yellow]")

    except websockets.exceptions.InvalidURI:
        console.print(f"[bold red]Error: Invalid WebSocket URI: {uri}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")


if __name__ == "__main__":
    print("This is an enhanced interactive client.")
    print("Please ensure you have installed the necessary libraries: pip install websockets prompt-toolkit rich")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\nClient shut down.")
