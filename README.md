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
- `rotors` (list[object]): List of `RotorConfig` objects. Each object specifies `rotor_type` (str), `ring_setting` (int, default=0), and `initial_position` (int | str, default=0). IMPORTANT: The list MUST be ordered from Fastest (Right) to Slowest (Left). For M4, the Greek rotor is the last element.
- `reflector` (object): A `ReflectorConfig` object specifying `reflector_type` (str), and optionally `ring_setting` (int) and `initial_position` (int | str) for rotating reflectors.
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
*(Note: Make sure you have built the Docker image first: `docker build -t enigma-mcp-server .`)*

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
To use this server with OpenCode, add the following to your `~/.config/opencode/opencode.json` (global) or `opencode.json` (project-level) under the `mcp` section:

### Using Python
```json
{
  "mcp": {
    "enigma": {
      "type": "local",
      "command": [
        "/absolute/path/to/enigma-python-mcp/server.py",
        "--transport",
        "stdio"
      ],
      "enabled": true
    }
  }
}
```

### Using Docker
*(Note: Make sure you have built the Docker image first: `docker build -t enigma-mcp-server .`)*

```json
{
  "mcp": {
    "enigma": {
      "type": "local",
      "command": [
        "docker",
        "run",
        "-i",
        "--rm",
        "enigma-mcp-server"
      ],
      "enabled": true
    }
  }
}
```

## Example Prompts
Once the server is configured, you can test it by sending the following prompts to your LLM:

**Example 1: Basic Encryption (Enigma M3)**
> "I need to encrypt the message 'TOPSECRET' using an Enigma M3. Please use rotors I, II, and III from left to right, all starting at position 0 with ring settings at 0. Use reflector 'UKWB' and no plugboard. What is the ciphertext?"

**Example 2: Historical Decryption (Enigma I)**
> "Decrypt this 1930 Enigma I message. The ciphertext is 'GCDSEAHUGWTQGRK'. The settings are: Rotors II, I, and III (Left to Right). Ring settings are 23, 12, and 21. Initial positions are 0, 1, and 11. The reflector is 'UKWA'. The plugboard swaps are: A/M, F/I, N/V, P/S, T/U, W/Z."

**Example 3: Complex M4 Configuration**
> "Use the Enigma M4 to encrypt the message 'DIVE DIVE DIVE'. The machine uses the 'UKWBThin' reflector. The rotors from left to right are: Gamma (pos 21), IV (pos 12), III (pos 6), and VIII (pos 2). All ring settings are 0. Please process this."

## Testing
A comprehensive test suite is included in `tests/test_server.py`. It tests the encryption and decryption reversibility for all 10 supported Enigma models.

To run the tests:
```bash
# Activate your virtual environment first
source .venv/bin/activate

pip install pytest
pytest tests/test_server.py
```
