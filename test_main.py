# test_main.py

import pytest
from fastapi.testclient import TestClient
from main import app  # Assuming your FastAPI app instance is named 'app' in 'main.py'

# Create a client to interact with the app in tests
client = TestClient(app)

def test_full_sandbox_lifecycle():
    """
    Tests the complete lifecycle of a sandbox:
    1. Create a sandbox.
    2. Execute a command in it.
    3. Delete the sandbox.
    """
    # 1. Create a new sandbox
    create_response = client.post("/sandboxes")
    assert create_response.status_code == 200, f"Failed to create sandbox. Response: {create_response.text}"
    response_data = create_response.json()
    assert "container_id" in response_data
    container_id = response_data["container_id"]
    
    # Ensure we got a valid container ID string
    assert isinstance(container_id, str)
    assert len(container_id) > 0

    # 2. Execute a command in the sandbox
    execute_payload = {"command": "echo 'hello world'"}
    execute_response = client.post(
        f"/sandboxes/{container_id}/execute",
        json=execute_payload
    )
    assert execute_response.status_code == 200, f"Failed to execute command. Response: {execute_response.text}"
    execute_data = execute_response.json()
    assert execute_data.get("output") == "hello world\n"
    assert execute_data.get("exit_code") == 0

    # 3. Delete the sandbox
    delete_response = client.delete(f"/sandboxes/{container_id}")
    assert delete_response.status_code == 200, f"Failed to delete sandbox. Response: {delete_response.text}"
    assert delete_response.json().get("message") == "Container removed"

    # Verify the container is gone by trying to execute another command
    verify_response = client.post(
        f"/sandboxes/{container_id}/execute",
        json=execute_payload
    )
    assert verify_response.status_code == 404
    assert verify_response.json().get("detail") == "Container not found"

def test_execute_in_nonexistent_container():
    """
    Tests that the API returns a 404 error when trying to execute
    a command in a container that does not exist.
    """
    non_existent_id = "a1b2c3d4e5f6_non_existent"
    execute_payload = {"command": "whoami"}
    response = client.post(
        f"/sandboxes/{non_existent_id}/execute",
        json=execute_payload
    )
    assert response.status_code == 404
    assert response.json().get("detail") == "Container not found"

def test_delete_nonexistent_container():
    """
    Tests that the API returns a 404 error when trying to delete
    a container that does not exist.
    """
    non_existent_id = "a1b2c3d4e5f6_non_existent"
    response = client.delete(f"/sandboxes/{non_existent_id}")
    assert response.status_code == 404
    assert response.json().get("detail") == "Container not found"
