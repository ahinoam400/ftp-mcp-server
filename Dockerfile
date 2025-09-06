
# Start from the base image
FROM python:3.13-slim

# Set the working directory inside the container.
WORKDIR /app

# Install system dependencies needed for some Python packages.
# The '--no-install-recommends' flag reduces the size of the image.
# We also clean up the package cache (the 'rm' command).
RUN apt-get update && \
    apt-get install -y --no-install-recommends npm && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file into the container.
COPY requirements.txt .

# Install the Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Install the Gemini CLI using npm.
RUN npm install -g @google/gemini-cli

# Copy the rest of your application code into the container.
COPY . .

# Create a Gemini settings directory and a settings file to configure the MCP server.
RUN mkdir -p /root/.gemini

# Copy the gemini's setting file - so when it starts, it will start the mcp server too.
COPY settings.json /root/.gemini/settings.json

# Expose port.
EXPOSE 8000
