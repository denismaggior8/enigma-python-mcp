# Enigma Python MCP Server

An MCP (Model Context Protocol) server that brings the capabilities of the [enigmapython](https://github.com/denismaggior8/enigma-python) library to LLMs, allowing them to encrypt and decrypt messages using historically accurate Enigma machine emulators.

## Features
- **Exposes all known Enigma machine models**: Enigma M3, Enigma M4, Enigma I, Enigma K, Enigma Z, Enigma D, and more.
- **Dynamic Configuration**: LLMs can specify rotors, initial positions, ring settings, reflectors, and plugboard pairs for the encryption.
- **Local and Network Mode**: Supports both `stdio` transport for local MCP integrations (like Claude Desktop) and `sse` transport to expose the tools over a network.
- **Dockerized**: Easy portability and execution across platforms.

## Exposed Tools

### `encrypt_message`
Encrypt or decrypt a message using a configured Enigma machine.

**Arguments:**
- `machine_model` (str): Model name. Supported: `'M3'`, `'M4'`, `'I'`, `'I_Norway'`, `'I_Sondermaschine'`, `'K'`, `'K_Swiss'`, `'D'`, `'Z'`, `'B_A133'`.
- `message` (str): The plaintext or ciphertext to process.
- `rotors` (list[object]): List of `RotorConfig` objects. Each object specifies `rotor_type` (str), `ring_setting` (int, default=0), and `initial_position` (int | str, default=0).
- `reflector` (str): The reflector identifier (e.g., `'UKWA'`, `'UKWB'`, `'UKWC'`, `'UKWBThin'`).
- `plugboard_pairs` (dict, optional): Dictionary mapping plugboard connections (e.g., `{"A": "B", "C": "D"}`).

## Running the Server

### Using Python
Requires Python 3.11+.

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run via stdio (for local MCP client):
   ```bash
   python server.py --transport stdio
   ```

3. Run via SSE (exposing over network):
   ```bash
   python server.py --transport sse --host 0.0.0.0 --port 8000
   ```

### Using Docker
1. Build the container:
   ```bash
   docker build -t enigma-mcp-server .
   ```

2. Run via stdio (default):
   ```bash
   docker run -i enigma-mcp-server
   ```

3. Run via SSE:
   ```bash
   docker run -p 8000:8000 enigma-mcp-server python server.py --transport sse --host 0.0.0.0 --port 8000
   ```

## Client Configuration (Claude Desktop)
To use this with Claude Desktop locally, add the following to your `claude_desktop_config.json`:

### Using Python
```json
{
  "mcpServers": {
    "enigma": {
      "command": "python",
      "args": ["/absolute/path/to/enigma-python-mcp/server.py", "--transport", "stdio"]
    }
  }
}
```

### Using Docker
```json
{
  "mcpServers": {
    "enigma": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "enigma-mcp-server"]
    }
  }
}
```

## Client Configuration (OpenCode)
To use this server with OpenCode, add the following to your `~/.config/opencode/opencode.jsonc` (global) or `opencode.json` (project-level) under the `mcp` section:

### Using Python
```json
{
  "mcp": {
    "enigma": {
      "type": "stdio",
      "command": "python",
      "args": ["/absolute/path/to/enigma-python-mcp/server.py", "--transport", "stdio"],
      "enabled": true
    }
  }
}
```

### Using Docker
```json
{
  "mcp": {
    "enigma": {
      "type": "stdio",
      "command": "docker",
      "args": ["run", "-i", "--rm", "enigma-mcp-server"],
      "enabled": true
    }
  }
}
```

## Testing
A comprehensive test suite is included in `tests/test_server.py`. It tests the encryption and decryption reversibility for all 10 supported Enigma models.

To run the tests:
```bash
# Activate your virtual environment first
source .venv/bin/activate

pip install pytest
pytest tests/test_server.py
```
