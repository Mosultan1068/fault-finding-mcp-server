# Start from a small, official Python base image.
# "slim" keeps the image size down compared to the full python image.
FROM python:3.11-slim

# Set the working directory inside the container.
# All following commands run relative to this folder.
WORKDIR /app

# Copy just the requirements file first (not the whole project yet).
# This is a deliberate ordering trick: Docker caches each step, so if
# your code changes but requirements.txt doesn't, Docker can reuse the
# cached "pip install" step instead of reinstalling everything from
# scratch every time. Faster rebuilds.
COPY requirements.txt .

# Install the Python dependencies inside the container.
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the project files (server.py, data/, etc.)
COPY . .

# Define the command that runs when a container is started from this image.
CMD ["python", "server.py"]