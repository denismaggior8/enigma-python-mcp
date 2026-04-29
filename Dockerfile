FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY server.py .

# By default run using stdio
# To run over SSE (network), override the CMD:
# CMD ["python", "server.py", "--transport", "sse"]
CMD ["python", "server.py", "--transport", "stdio"]
