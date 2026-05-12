# ItchWHMMCP

A local Model Context Protocol (MCP) server for managing WHM and cPanel servers through MCP-compatible AI clients. It supports multiple WHM accounts from a private local configuration file and exposes server health, account, DNS, email, database, SSL, bandwidth, disk, cron, and service-management tools.

> Security warning: this server can perform root-level WHM actions. Run it only on machines and with AI clients you trust, scope WHM API tokens as tightly as your workflow allows, and confirm destructive actions before execution.

---

## Compatible Clients

| Client | Config File | Notes |
|---|---|---|
| [Claude Desktop](https://claude.ai/download) | `claude_desktop_config.json` | Full support |
| [Cursor](https://cursor.sh) | `.cursor/mcp.json` | Full support |
| [Windsurf](https://codeium.com/windsurf) | `~/.codeium/windsurf/mcp_config.json` | Full support |
| [VS Code + Copilot](https://code.visualstudio.com) | `.vscode/mcp.json` | Requires MCP support/extension |
| [Cline](https://github.com/cline/cline) | MCP settings UI | Full support |
| [Continue](https://continue.dev) | `config.json` | Full support |
| Any stdio MCP host | Client-specific | Standard stdio transport |

---

## Features

| Category | Capabilities |
|---|---|
| Server Health | Load averages, memory, CPU, uptime |
| Account Management | List, create, suspend, unsuspend, terminate cPanel accounts |
| DNS | List zones and query records per domain |
| MySQL | List databases across the server |
| Bandwidth | Usage per account or server-wide |
| SSL | List installed certificates |
| Services | Check and restart Apache, MySQL, Exim, FTP |
| Email | List and create mailboxes, list forwarders |
| Disk | Server-wide and per-account disk usage |
| Cron Jobs | List scheduled tasks per cPanel account |
| Subdomains | List subdomains and addon domains |

The server currently exposes 30 tools across WHM root-level and cPanel account-level operations.

---

## Requirements

- Python 3.11+
- An MCP-compatible AI client
- WHM server access with an API token

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/manofsadness/ItchWHMMCP.git
cd ItchWHMMCP
```

### 2. Create a virtual environment

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install mcp httpx
```

---

## Configuration

### Step 1 - Generate WHM API Tokens

For each server you want to connect:

1. Log in to WHM.
2. Open Development > Manage API Tokens.
3. Generate a token for this MCP server.
4. Copy the token immediately; WHM shows it only once.
5. Repeat for each server you want to manage.

### Step 2 - Create your private accounts file

```bash
cp accounts.json.template accounts.json
```

Edit `accounts.json` with your own server details:

```json
{
  "primary-server": {
    "host": "server.example.com",
    "port": 2087,
    "user": "root",
    "token": "YOUR_WHM_API_TOKEN_HERE",
    "type": "whm",
    "label": "Primary WHM Server"
  },
  "staging-server": {
    "host": "staging.example.com",
    "port": 2087,
    "user": "root",
    "token": "YOUR_SECOND_WHM_API_TOKEN_HERE",
    "type": "whm",
    "label": "Staging WHM Server"
  }
}
```

Never commit `accounts.json`, API tokens, real hostnames, IP addresses, client names, or production account aliases.

---

## Client Setup

All clients need the same two values:

- `command`: the Python executable inside `.venv`
- `args`: the path to `src/server.py`

Use absolute paths in client configuration files.

### Claude Desktop

Config file location:

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

```json
{
  "mcpServers": {
    "ItchWHMMCP": {
      "command": "/absolute/path/to/ItchWHMMCP/.venv/bin/python",
      "args": ["/absolute/path/to/ItchWHMMCP/src/server.py"]
    }
  }
}
```

### Cursor

Create or edit `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "ItchWHMMCP": {
      "command": "/absolute/path/to/ItchWHMMCP/.venv/bin/python",
      "args": ["/absolute/path/to/ItchWHMMCP/src/server.py"]
    }
  }
}
```

### Windsurf

Edit `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "ItchWHMMCP": {
      "command": "/absolute/path/to/ItchWHMMCP/.venv/bin/python",
      "args": ["/absolute/path/to/ItchWHMMCP/src/server.py"]
    }
  }
}
```

### VS Code

Create `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "ItchWHMMCP": {
      "type": "stdio",
      "command": "/absolute/path/to/ItchWHMMCP/.venv/bin/python",
      "args": ["/absolute/path/to/ItchWHMMCP/src/server.py"]
    }
  }
}
```

### Cline

Open Cline settings > MCP Servers > Add Server, choose stdio, then enter:

- Command: `/absolute/path/to/ItchWHMMCP/.venv/bin/python`
- Args: `/absolute/path/to/ItchWHMMCP/src/server.py`

### Continue

Add to `~/.continue/config.json`:

```json
{
  "mcpServers": [
    {
      "name": "ItchWHMMCP",
      "command": "/absolute/path/to/ItchWHMMCP/.venv/bin/python",
      "args": ["/absolute/path/to/ItchWHMMCP/src/server.py"]
    }
  ]
}
```

### Any Other stdio MCP Host

Use `mcp.json` in the project root as a reference:

```json
{
  "name": "ItchWHMMCP",
  "version": "1.0.0",
  "transport": "stdio",
  "command": "python",
  "args": ["src/server.py"]
}
```

Windows users should replace `.venv/bin/python` with `.venv\Scripts\python.exe`.

---

## Usage Examples

Once connected, ask your AI client naturally:

```text
List all configured WHM accounts
Check server load on primary-server
Show DNS records for example.com on primary-server
Is Apache running on staging-server?
List email accounts for user demo on primary-server
Check disk usage across all accounts on primary-server
Suspend account demo-user on staging-server for policy violation
Show all SSL certificates on primary-server
What cron jobs does user demo have on primary-server?
```

Confirm the target server and account before running write operations such as account creation, suspension, termination, password changes, or service restarts.

---

## Adding More Servers

Add another entry to `accounts.json` and restart your AI client. No code changes are required.

---

## Project Structure

```text
ItchWHMMCP/
|-- src/
|   |-- server.py          # MCP entry point
|   |-- accounts.py        # Multi-account loader
|   `-- tools.py           # WHM and cPanel tool definitions/handlers
|-- accounts.json.template # Safe template to copy from
|-- mcp.json               # Generic MCP client reference config
|-- pyproject.toml
|-- CONTRIBUTING.md
|-- LICENSE
`-- README.md
```

Local-only files such as `accounts.json`, `.env`, virtual environments, AI-agent notes, and personal client configuration should remain untracked.

---

## Security Notes

- WHM API tokens can be scoped and revoked per server from WHM.
- `accounts.json` must stay local and untracked.
- Avoid publishing real hostnames, IP addresses, account names, client names, API tokens, screenshots, or log output.
- SSL verification is disabled by default for self-signed WHM certificates. If your server has a trusted certificate, enable verification in `src/tools.py`.
- The MCP server runs locally as a subprocess of your AI client and does not open an inbound network port.
- Review every destructive action before approving it in an AI client.

---

## Contributing

Pull requests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.

---

## License

MIT - see [LICENSE](LICENSE) for details.
