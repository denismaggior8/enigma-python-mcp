# Changelog

All notable changes to this project will be documented in this file.

## [0.1.2] - 2026-04-30

### Fixed
- **Integer Type Coercion**: Fixed an issue where numeric string messages (e.g., `1234567890`) passed to numerical Enigma machines (like the Enigma Z) would fail Pydantic validation because they were interpreted as raw integers in JSON. The `message` parameter now natively accepts both `str` and `int`.
- **Character Validation Feedback**: Fixed an issue where an LLM passing literal quotes (e.g., `"1234567890"`) or spaces would cause a cryptic `ValueError: '"' is not in list`. The server now intercepts these character errors and returns a highly actionable error message explicitly telling the LLM to strip spaces, punctuation, and literal quotes before resubmitting.
- **Enigma Z Electrical Short Circuit**: Fixed a catastrophic crash where the LLM could hallucinate an alphabetic A-Z reflector (like `UKWB`) for the purely numeric `Enigma Z` model. The incompatible wiring would cause `enigmapython` to crash deep in the simulation with `ValueError: 'y' is not in list`. The MCP server now actively validates the reflector type during instantiation and immediately raises a helpful error if it detects an alphabetic reflector being wired into a numeric machine.


## [0.1.1] - 2026-04-30

### Added
- **Robust LLM Input Sanitization**: Vastly improved resilience against LLM prompt formatting hallucinations:
  - **Machine Models**: Gracefully handles prefixes, spaces, and hyphens (e.g., `"Enigma I-Norway"` maps cleanly to `"I_Norway"`).
  - **Rotors**: Strips the word "Rotor" and gracefully handles casing and hyphens (e.g., `"Rotor-III"`, `"beta"` map cleanly to `"III"`, `"Beta"`).
  - **Reflectors**: Added an explicit alias map to handle common spacing issues (e.g., `"UKW A"`, `"UKW-B Thin"` map cleanly to `"UKWA"`, `"UKWBThin"`).
- **Repository Badges**: Added dynamic shields.io and pepy.tech badges to the `README.md` tracking PyPI version, downloads, Python compatibility, and build status.

### Changed
- Refactored `manifest.json` into two discrete manifests (`manifest-docker.json` and `manifest-python.json`) to cleanly support the dual `.mcpb` build strategy.

## [0.1.0] - 2026-04-29

### Added
- Initial packaging release of `enigmapython-mcp`.
- Migrated core server logic to a `src/enigmapython_mcp/` structure.
- Implemented `pyproject.toml` (managed by hatchling) with dynamic dependencies.
- Registered the console script entry point `enigmapython-mcp`.
- **Automated CI Tests**: Integrated the `pytest` suite directly into the GitHub Actions pipeline to prevent publishing broken packages.
- **Automated PyPI Publishing**: Configured GitHub Actions (`publish.yml`) to automatically publish the `enigmapython-mcp` package to PyPI using PyPI Trusted Publishing (OIDC).
- **Dual MCP Bundles**: The GitHub Release pipeline now automatically generates two distinct `.mcpb` bundles for Claude Desktop:
  - `enigmapython-mcp-docker.mcpb`: A lightweight configuration that relies on the local Docker daemon.
  - `enigmapython-mcp-python.mcpb`: A self-contained bundle that natively builds a Python virtual environment without requiring Docker.
