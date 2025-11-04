# 1. Create a new sandbox
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/sandboxes" -Method Post
$container_id = ($response.Content | ConvertFrom-Json).container_id
Write-Host "Created container with ID: $container_id"

# 2. Execute a command in the sandbox
$command = @{ command = "ls -la" } | ConvertTo-Json
Invoke-WebRequest -Uri "http://127.0.0.1:8000/sandboxes/$container_id/execute" -Method Post -Body $command -ContentType "application/json"

# 3. Remove the sandbox
Invoke-WebRequest -Uri "http://127.0.0.1:8000/sandboxes/$container_id" -Method Delete
