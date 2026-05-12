"""
Account configuration loader.
Supports multiple WHM/cPanel accounts via:
  1. accounts.json file (recommended for multi-account)
  2. Environment variables (single account fallback)
"""

import json
import os
from pathlib import Path

_ACCOUNTS: dict | None = None

CONFIG_PATH = Path(__file__).parent.parent / "accounts.json"


def load_accounts() -> dict:
    global _ACCOUNTS
    if _ACCOUNTS is not None:
        return _ACCOUNTS

    # Try accounts.json first
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            _ACCOUNTS = json.load(f)
        return _ACCOUNTS

    # Fall back to environment variables (single account)
    host = os.environ.get("WHM_HOST")
    user = os.environ.get("WHM_USER", "root")
    token = os.environ.get("WHM_TOKEN")

    if host and token:
        _ACCOUNTS = {
            "default": {
                "host": host,
                "user": user,
                "token": token,
                "type": "whm",
                "port": int(os.environ.get("WHM_PORT", "2087"))
            }
        }
    else:
        _ACCOUNTS = {}

    return _ACCOUNTS


def get_account(alias: str) -> dict | None:
    accounts = load_accounts()
    return accounts.get(alias)
