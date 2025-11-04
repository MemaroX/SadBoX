# Use a minimal Python 3.10 base image
FROM python:3.10-slim

# Create a non-root user
RUN useradd -m sandboxuser

# Set the user
USER sandboxuser

# Keep the container running and open a bash shell
CMD ["/bin/bash"]
