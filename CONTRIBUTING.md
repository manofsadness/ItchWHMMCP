# Contributing to ItchWHMMCP

Thank you for your interest in contributing!

## How to Contribute

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test against a real WHM server if possible
5. Submit a pull request with a clear description of what changed and why

## Adding New Tools

All tools are defined in `src/tools.py`. To add a new tool:

1. Add a `Tool(...)` entry in either `whm_tools()` or `cpanel_tools()`
2. Add the corresponding `case` handler in `handle_whm_tool()` or `handle_cpanel_tool()`
3. Reference the [WHM API documentation](https://api.docs.cpanel.net/openapi/whm/operation/) or [cPanel UAPI documentation](https://api.docs.cpanel.net/openapi/cpanel/operation/) for available endpoints

## Guidelines

- Keep tools focused and single-purpose
- Use descriptive tool names with the `whm_` or `cpanel_` prefix
- Always include an `account` parameter so multi-account routing works
- Never hardcode credentials, hostnames, or user-specific values
- Document any new dependencies in `pyproject.toml`

## Reporting Issues

Open a GitHub issue with:
- Your OS and Python version
- The tool name that failed
- The error message from Claude Desktop logs
- Your WHM version if known
