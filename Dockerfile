FROM python:3.11-slim

WORKDIR /app

# Install dependencies and the package itself
COPY . .
RUN pip install --no-cache-dir .

# Run the server via the console script
ENTRYPOINT ["enigmapython-mcp"]

# By default run using stdio
# To run over SSE (network), override the CMD:
# CMD ["--transport", "sse"]
CMD ["--transport", "stdio"]
