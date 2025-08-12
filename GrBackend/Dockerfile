# Stage 1: Builder stage to install dependencies
FROM python:3.12-slim AS builder

# Install system dependencies, download and extract Blender
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libxext6 libxrender1 libx11-6 libxi6 libgl1 libgl1-mesa-glx libglib2.0-0 libxkbcommon0 libsm6 \
    wget tar xz-utils && \
    wget https://download.blender.org/release/Blender4.2/blender-4.2.2-linux-x64.tar.xz && \
    tar -xvf blender-4.2.2-linux-x64.tar.xz && \
    mv blender-4.2.2-linux-x64 /opt/blender && \
    rm blender-4.2.2-linux-x64.tar.xz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install uv

WORKDIR /app

# Copy only the dependency definition to leverage Docker layer caching
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv pip install --system --no-cache-dir -r pyproject.toml


# Stage 2: Final application image
FROM python:3.12-slim

# Install system dependencies required for Blender
RUN apt-get update && apt-get install -y libxext6 libxrender1 libx11-6 libxi6 libgl1 libgl1-mesa-glx libglib2.0-0 libxkbcommon0 libsm6 libegl1

WORKDIR /app

# Copy Blender from the builder stage
COPY --from=builder /opt/blender /opt/blender

# Set Blender executable path
ENV PATH="/opt/blender:${PATH}"

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy the application code
# This copies the entire GrBackend directory context
COPY . .

# --- Install Blender Add-on ---
# 1. Copy the addon .zip file and the installation script into the container
COPY blend_file/productvideo-1.0.11.zip .
COPY blender_script/install_addon.py .

# 2. Run Blender in the background to execute the script, then clean up
RUN /opt/blender/blender --background --python install_addon.py && \
    rm install_addon.py productvideo-1.0.11.zip
# --- END Add-on Install SECTION ---

# Expose the port the Gradio app runs on (default is 7860)
EXPOSE 8030

# The command to run when the container starts
CMD ["python", "app.py"]