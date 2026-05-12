"""
Tool definitions and handlers for WHM (root) and cPanel (account-level) operations.
"""

import httpx
from mcp.types import Tool

# ─── Shared helpers ────────────────────────────────────────────────────────────

def _whm_url(account: dict, function: str) -> str:
    host = account["host"]
    port = account.get("port", 2087)
    user = account.get("user", "root")
    return f"https://{host}:{port}/json-api/{function}?api.version=1"


def _cpanel_url(account: dict, module: str, function: str, cpanel_user: str = None) -> str:
    host = account["host"]
    port = account.get("port", 2087)
    # WHM-proxied UAPI call on behalf of a cPanel user
    user = cpanel_user or account.get("cpanel_user", "")
    return f"https://{host}:{port}/json-api/cpanel?api.version=1&cpanel_jsonapi_user={user}&cpanel_jsonapi_module={module}&cpanel_jsonapi_func={function}&cpanel_jsonapi_apiversion=3"


def _headers(account: dict) -> dict:
    token = account["token"]
    user = account.get("user", "root")
    return {
        "Authorization": f"whm {user}:{token}"
    }


async def _get(client: httpx.AsyncClient, url: str, headers: dict, params: dict = None) -> dict:
    try:
        kwargs = {"headers": headers}
        if params is not None:
            kwargs["params"] = params
        r = await client.get(url, **kwargs)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        return {
            "error": str(e),
            "status_code": e.response.status_code,
            "response": e.response.text[:1000],
        }
    except Exception as e:
        return {"error": str(e)}


async def _post(client: httpx.AsyncClient, url: str, headers: dict, data: dict = None) -> dict:
    try:
        kwargs = {"headers": headers}
        if data is not None:
            kwargs["json"] = data
        r = await client.post(url, **kwargs)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        return {
            "error": str(e),
            "status_code": e.response.status_code,
            "response": e.response.text[:1000],
        }
    except Exception as e:
        return {"error": str(e)}


# ─── Account param (shared by all tools) ───────────────────────────────────────

ACCOUNT_PARAM = {
    "account": {
        "type": "string",
        "description": "Account alias from accounts.json (use list_accounts to see options)"
    }
}

# ─── WHM Tool Definitions ──────────────────────────────────────────────────────

def whm_tools() -> list[Tool]:
    return [
        Tool(
            name="whm_server_info",
            description="Get WHM server information: hostname, OS, cPanel version, load, uptime",
            inputSchema={
                "type": "object",
                "properties": ACCOUNT_PARAM,
                "required": ["account"]
            }
        ),
        Tool(
            name="whm_list_accounts",
            description="List all cPanel accounts on this WHM server with disk usage, domain, status",
            inputSchema={
                "type": "object",
                "properties": {**ACCOUNT_PARAM},
                "required": ["account"]
            }
        ),
        Tool(
            name="whm_account_summary",
            description="Get detailed summary for a specific cPanel account (disk, bandwidth, emails, DBs)",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "username": {"type": "string", "description": "cPanel username to inspect"}
                },
                "required": ["account", "username"]
            }
        ),
        Tool(
            name="whm_create_account",
            description="Create a new cPanel hosting account on the WHM server",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "username": {"type": "string"},
                    "domain": {"type": "string"},
                    "password": {"type": "string"},
                    "email": {"type": "string"},
                    "plan": {"type": "string", "description": "Hosting plan name (optional)"}
                },
                "required": ["account", "username", "domain", "password", "email"]
            }
        ),
        Tool(
            name="whm_suspend_account",
            description="Suspend a cPanel account (disables login, web, email)",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "username": {"type": "string"},
                    "reason": {"type": "string", "description": "Reason for suspension"}
                },
                "required": ["account", "username"]
            }
        ),
        Tool(
            name="whm_unsuspend_account",
            description="Unsuspend/reactivate a suspended cPanel account",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "username": {"type": "string"}
                },
                "required": ["account", "username"]
            }
        ),
        Tool(
            name="whm_change_password",
            description="Change password for a cPanel account",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "username": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["account", "username", "password"]
            }
        ),
        Tool(
            name="whm_terminate_account",
            description="⚠️ PERMANENTLY DELETE a cPanel account and all its data",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "username": {"type": "string"},
                    "confirm": {"type": "boolean", "description": "Must be true to confirm deletion"}
                },
                "required": ["account", "username", "confirm"]
            }
        ),
        Tool(
            name="whm_server_load",
            description="Get real-time server load averages, memory usage, CPU, swap",
            inputSchema={
                "type": "object",
                "properties": ACCOUNT_PARAM,
                "required": ["account"]
            }
        ),
        Tool(
            name="whm_disk_usage",
            description="Get disk usage breakdown across all accounts on the server",
            inputSchema={
                "type": "object",
                "properties": ACCOUNT_PARAM,
                "required": ["account"]
            }
        ),
        Tool(
            name="whm_list_packages",
            description="List all hosting packages/plans configured on the WHM server",
            inputSchema={
                "type": "object",
                "properties": ACCOUNT_PARAM,
                "required": ["account"]
            }
        ),
        Tool(
            name="whm_list_ips",
            description="List all IP addresses on the server and their assignments",
            inputSchema={
                "type": "object",
                "properties": ACCOUNT_PARAM,
                "required": ["account"]
            }
        ),
        Tool(
            name="whm_dns_list_zones",
            description="List all DNS zones managed by this WHM server",
            inputSchema={
                "type": "object",
                "properties": ACCOUNT_PARAM,
                "required": ["account"]
            }
        ),
        Tool(
            name="whm_dns_zone_records",
            description="Get all DNS records for a specific zone/domain",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "domain": {"type": "string", "description": "Domain name to query"}
                },
                "required": ["account", "domain"]
            }
        ),
        Tool(
            name="whm_mysql_list_dbs",
            description="List all MySQL databases on the server across all accounts",
            inputSchema={
                "type": "object",
                "properties": ACCOUNT_PARAM,
                "required": ["account"]
            }
        ),
        Tool(
            name="whm_bandwidth_usage",
            description="Get bandwidth usage statistics for all accounts or a specific account",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "username": {"type": "string", "description": "Filter by cPanel username (optional)"}
                },
                "required": ["account"]
            }
        ),
        Tool(
            name="whm_list_services",
            description="Check status of all WHM services (Apache, MySQL, cPanel, SMTP, etc.)",
            inputSchema={
                "type": "object",
                "properties": ACCOUNT_PARAM,
                "required": ["account"]
            }
        ),
        Tool(
            name="whm_restart_service",
            description="Restart a specific service on the WHM server (apache, mysql, exim, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "service": {"type": "string", "description": "Service name: apache, mysql, exim, ftp, cpsrvd"}
                },
                "required": ["account", "service"]
            }
        ),
        Tool(
            name="whm_ssl_list",
            description="List all SSL certificates installed on the server",
            inputSchema={
                "type": "object",
                "properties": ACCOUNT_PARAM,
                "required": ["account"]
            }
        ),
        Tool(
            name="whm_backup_list",
            description="List available backups on the WHM server",
            inputSchema={
                "type": "object",
                "properties": ACCOUNT_PARAM,
                "required": ["account"]
            }
        ),
    ]


# ─── cPanel Tool Definitions (account-level) ──────────────────────────────────

def cpanel_tools() -> list[Tool]:
    return [
        Tool(
            name="cpanel_email_list",
            description="List all email accounts for a cPanel user's domain",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "cpanel_user": {"type": "string", "description": "cPanel username"},
                    "domain": {"type": "string", "description": "Domain to list emails for"}
                },
                "required": ["account", "cpanel_user", "domain"]
            }
        ),
        Tool(
            name="cpanel_email_create",
            description="Create a new email account for a cPanel user",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "cpanel_user": {"type": "string"},
                    "email": {"type": "string", "description": "Full email address"},
                    "password": {"type": "string"},
                    "quota": {"type": "integer", "description": "Mailbox quota in MB (0 = unlimited)"}
                },
                "required": ["account", "cpanel_user", "email", "password"]
            }
        ),
        Tool(
            name="cpanel_forwarders_list",
            description="List all email forwarders for a cPanel user's domain",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "cpanel_user": {"type": "string"},
                    "domain": {"type": "string"}
                },
                "required": ["account", "cpanel_user", "domain"]
            }
        ),
        Tool(
            name="cpanel_dns_records",
            description="Get DNS zone records for a domain via cPanel UAPI",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "cpanel_user": {"type": "string"},
                    "domain": {"type": "string"}
                },
                "required": ["account", "cpanel_user", "domain"]
            }
        ),
        Tool(
            name="cpanel_mysql_list",
            description="List MySQL databases and users for a cPanel account",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "cpanel_user": {"type": "string"}
                },
                "required": ["account", "cpanel_user"]
            }
        ),
        Tool(
            name="cpanel_disk_usage",
            description="Get disk usage breakdown for a specific cPanel account",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "cpanel_user": {"type": "string"}
                },
                "required": ["account", "cpanel_user"]
            }
        ),
        Tool(
            name="cpanel_ssl_check",
            description="Check SSL certificate status and expiry for a cPanel account's domains",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "cpanel_user": {"type": "string"}
                },
                "required": ["account", "cpanel_user"]
            }
        ),
        Tool(
            name="cpanel_cron_list",
            description="List all cron jobs configured for a cPanel account",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "cpanel_user": {"type": "string"}
                },
                "required": ["account", "cpanel_user"]
            }
        ),
        Tool(
            name="cpanel_subdomains_list",
            description="List all subdomains and addon domains for a cPanel account",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "cpanel_user": {"type": "string"}
                },
                "required": ["account", "cpanel_user"]
            }
        ),
        Tool(
            name="cpanel_bandwidth_usage",
            description="Get bandwidth usage stats for a specific cPanel account",
            inputSchema={
                "type": "object",
                "properties": {
                    **ACCOUNT_PARAM,
                    "cpanel_user": {"type": "string"}
                },
                "required": ["account", "cpanel_user"]
            }
        ),
    ]


# ─── WHM Tool Handlers ─────────────────────────────────────────────────────────

async def handle_whm_tool(client: httpx.AsyncClient, account: dict, name: str, args: dict) -> dict:
    url_base = _whm_url(account, "")
    headers = _headers(account)

    def url(fn): return _whm_url(account, fn)

    match name:
        case "whm_server_info":
            return await _get(client, url("version"), headers)

        case "whm_list_accounts":
            return await _get(client, url("listaccts"), headers)

        case "whm_account_summary":
            return await _get(client, url("accountsummary"), headers, {"user": args["username"]})

        case "whm_create_account":
            params = {
                "username": args["username"],
                "domain": args["domain"],
                "password": args["password"],
                "contactemail": args["email"],
            }
            if "plan" in args:
                params["plan"] = args["plan"]
            return await _get(client, url("createacct"), headers, params)

        case "whm_suspend_account":
            params = {"user": args["username"]}
            if "reason" in args:
                params["reason"] = args["reason"]
            return await _get(client, url("suspendacct"), headers, params)

        case "whm_unsuspend_account":
            return await _get(client, url("unsuspendacct"), headers, {"user": args["username"]})

        case "whm_change_password":
            return await _get(client, url("passwd"), headers, {
                "user": args["username"],
                "password": args["password"]
            })

        case "whm_terminate_account":
            if not args.get("confirm"):
                return {"error": "You must set confirm=true to permanently delete an account. This is irreversible."}
            return await _get(client, url("removeacct"), headers, {"user": args["username"]})

        case "whm_server_load":
            return await _get(client, url("loadavg"), headers)

        case "whm_disk_usage":
            return await _get(client, url("getdiskusage"), headers)

        case "whm_list_packages":
            return await _get(client, url("listpkgs"), headers)

        case "whm_list_ips":
            return await _get(client, url("listips"), headers)

        case "whm_dns_list_zones":
            return await _get(client, url("listzones"), headers)

        case "whm_dns_zone_records":
            return await _get(client, url("dumpzone"), headers, {"domain": args["domain"]})

        case "whm_mysql_list_dbs":
            return await _get(client, url("listmysqldatabases"), headers)

        case "whm_bandwidth_usage":
            params = {}
            if "username" in args:
                params["user"] = args["username"]
            return await _get(client, url("getbwusage"), headers, params)

        case "whm_list_services":
            return await _get(client, url("servicestatus"), headers)

        case "whm_restart_service":
            service_map = {
                "apache": "httpd",
                "mysql": "mysql",
                "exim": "exim",
                "ftp": "ftpd",
                "cpsrvd": "cpsrvd"
            }
            svc = service_map.get(args["service"].lower(), args["service"])
            return await _get(client, url("restartservice"), headers, {"service": svc})

        case "whm_ssl_list":
            return await _get(client, url("fetchsslinfo"), headers)

        case "whm_backup_list":
            return await _get(client, url("backup_set_up_config"), headers)

        case _:
            return {"error": f"Unknown WHM tool: {name}"}


# ─── cPanel Tool Handlers ──────────────────────────────────────────────────────

async def handle_cpanel_tool(client: httpx.AsyncClient, account: dict, name: str, args: dict) -> dict:
    headers = _headers(account)
    cpanel_user = args.get("cpanel_user", "")

    def url(module, function):
        return _cpanel_url(account, module, function, cpanel_user)

    match name:
        case "cpanel_email_list":
            return await _get(client, url("Email", "list_pops"), headers, {"domain": args.get("domain", "")})

        case "cpanel_email_create":
            email_parts = args["email"].split("@")
            return await _get(client, url("Email", "add_pop"), headers, {
                "email": email_parts[0],
                "domain": email_parts[1] if len(email_parts) > 1 else "",
                "password": args["password"],
                "quota": args.get("quota", 0)
            })

        case "cpanel_forwarders_list":
            return await _get(client, url("Email", "list_forwarders"), headers, {"domain": args.get("domain", "")})

        case "cpanel_dns_records":
            return await _get(client, url("DNS", "parse_zone"), headers, {"zone": args["domain"]})

        case "cpanel_mysql_list":
            dbs = await _get(client, url("Mysql", "list_databases"), headers)
            users = await _get(client, url("Mysql", "list_users"), headers)
            return {"databases": dbs, "users": users}

        case "cpanel_disk_usage":
            return await _get(client, url("Quota", "get_quota_info"), headers)

        case "cpanel_ssl_check":
            return await _get(client, url("SSL", "list_certs"), headers)

        case "cpanel_cron_list":
            return await _get(client, url("Cron", "list_cron"), headers)

        case "cpanel_subdomains_list":
            subs = await _get(client, url("SubDomain", "list_subdomains"), headers)
            addons = await _get(client, url("AddonDomain", "list_addon_domains"), headers)
            return {"subdomains": subs, "addon_domains": addons}

        case "cpanel_bandwidth_usage":
            return await _get(client, url("StatsBar", "get_stats"), headers, {"display": "bandwidthusage"})

        case _:
            return {"error": f"Unknown cPanel tool: {name}"}
