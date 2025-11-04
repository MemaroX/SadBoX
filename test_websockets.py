# test_websockets.py

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_websocket_interaction():
    """
    Tests the WebSocket endpoint for interactive command execution.
    """
    # Step 1: Create a sandbox to interact with
    create_response = client.post("/sandboxes")
    assert create_response.status_code == 200, f"Failed to create sandbox: {create_response.text}"
    container_id = create_response.json()["container_id"]

    try:
        # Step 2: Connect to the WebSocket endpoint
        with client.websocket_connect(f"/sandboxes/{container_id}/ws") as websocket:
            # Step 3: Send a command and check the output
            websocket.send_text("echo 'hello from websocket'\n")
            response = websocket.receive_text()
            # The output might have some shell prompt artifacts, so we check for containment
            assert "hello from websocket" in response

            # Step 4: Send another command to test interactivity
            websocket.send_text("whoami\n")
            response = websocket.receive_text()
            assert "sandboxuser" in response

finally:
        # Step 5: Clean up the container
        delete_response = client.delete(f"/sandboxes/{container_id}")
        assert delete_response.status_code == 200, f"Failed to clean up sandbox: {delete_response.text}"

def test_websocket_with_nonexistent_container():
    """
    Tests that the WebSocket connection is rejected for a container that does not exist.
    """
    non_existent_id = "a1b2c3d4e5f6_non_existent"
    with pytest.raises(Exception) as excinfo:
         with client.websocket_connect(f"/sandboxes/{non_existent_id}/ws") as websocket:
            # This part of the code should not be reached
            pytest.fail("WebSocket connection to non-existent container should fail")
    # Check that the exception is a WebSocket close error
    assert "1011" in str(excinfo.value) # 1011 is the internal error code for container not found
