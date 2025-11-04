import docker
from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel
import asyncio
from config import settings # Import settings

app = FastAPI()
client = docker.from_env()

class Command(BaseModel):
    command: str

@app.post("/sandboxes")
async def create_sandbox():
    try:
        container = client.containers.run(
            settings.sandbox_image_name, # Use the setting here
            detach=True,
            mem_limit="256m",
            tty=True, # Keep container running
        )
        return {"container_id": container.id}
    except docker.errors.ImageNotFound:
        raise HTTPException(status_code=404, detail=f"Image '{settings.sandbox_image_name}' not found")

@app.post("/sandboxes/{container_id}/execute")
async def execute_command(container_id: str, command: Command):
    try:
        container = client.containers.get(container_id)
        exit_code, output = container.exec_run(command.command)
        return {"output": output.decode("utf-8"), "exit_code": exit_code}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")

@app.delete("/sandboxes/{container_id}")
async def remove_sandbox(container_id: str):
    try:
        container = client.containers.get(container_id)
        container.stop()
        container.remove()
        return {"message": "Container removed"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")

@app.websocket("/sandboxes/{container_id}/ws")
async def websocket_endpoint(websocket: WebSocket, container_id: str):
    await websocket.accept()
    try:
        container = client.containers.get(container_id)
        s = container.attach_socket(params={'stdin': 1, 'stream': 1, 'stdout': 1, 'stderr': 1})
        
        async def read_from_container(s, websocket):
            loop = asyncio.get_event_loop()
            while True:
                try:
                    output = await loop.sock_recv(s._sock, 1024)
                    if not output:
                        break
                    await websocket.send_text(output.decode('utf-8'))
                except Exception:
                    break

        async def write_to_container(s, websocket):
            while True:
                try:
                    data = await websocket.receive_text()
                    s._sock.sendall(data.encode('utf-8'))
                except Exception:
                    break

        read_task = asyncio.create_task(read_from_container(s, websocket))
        write_task = asyncio.create_task(write_to_container(s, websocket))

        await asyncio.gather(read_task, write_task)

    except docker.errors.NotFound:
        await websocket.close(code=1011, reason="Container not found")
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
