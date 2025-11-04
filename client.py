import asyncio
import websockets
import json

async def main():
    container_id = input("Enter the container ID: ")
    uri = f"ws://127.0.0.1:8000/sandboxes/{container_id}/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            command = input("Enter command: ")
            await websocket.send(command + "\n")
            response = await websocket.recv()
            # Format the output to look like the user's request
            output_json = json.dumps({"output": response})
            print(f"Content : {output_json}")

if __name__ == "__main__":
    print("To install websockets library, run: pip install websockets")
    print("To run the script, run: python client.py")
    asyncio.run(main())
