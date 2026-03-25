FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
WORKDIR /app

# Configure UV for container environment
ENV UV_SYSTEM_PYTHON=1 UV_COMPILE_BYTECODE=1



COPY requirements.txt requirements.txt
# Install from requirements file
RUN uv pip install -r requirements.txt




RUN uv pip install aws-opentelemetry-distro>=0.10.1


# Set AWS region environment variable

ENV AWS_REGION=us-east-1
ENV AWS_DEFAULT_REGION=us-east-1


# Signal that this is running in Docker for host binding logic
ENV DOCKER_CONTAINER=1

# Install Playwright Chromium and system dependencies (as root)
RUN python -m playwright install --with-deps chromium

# Skip Playwright install at runtime since browsers are pre-installed
ENV NOVA_ACT_SKIP_PLAYWRIGHT_INSTALL=1

# Create non-root user
RUN useradd -m -u 1000 bedrock_agentcore
RUN mkdir -p /home/bedrock_agentcore/.cache && \
    cp -r /root/.cache/ms-playwright /home/bedrock_agentcore/.cache/ms-playwright && \
    chown -R bedrock_agentcore:bedrock_agentcore /home/bedrock_agentcore/.cache

USER bedrock_agentcore

EXPOSE 8080
EXPOSE 8000

# Copy entire project (respecting .dockerignore)
COPY . .

# Use the full module path

CMD ["opentelemetry-instrument", "python", "-m", "first_stage_agent"]
