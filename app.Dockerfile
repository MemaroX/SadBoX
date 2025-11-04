# Step 1: Use a Python base image
FROM python:3.10-slim

# Step 2: Set the working directory
WORKDIR /app

# Step 3: Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the application code
COPY . .

# Step 5: Expose the port the app runs on
EXPOSE 8000

# Step 6: Define the command to run the application
# We also need to install the Docker daemon in the container to be able to create sandboxes
# This is a more advanced use case, for now we will assume the host's docker is used.
# A better solution would be to mount the docker socket.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
