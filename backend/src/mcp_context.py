"""Shared context variable so MCP tools can read the authenticated API key."""

import contextvars
from typing import Optional

# Set by the MCP auth middleware in app.py before each MCP request is handled.
# MCP tools read this to track per-key usage and enforce quotas.
mcp_api_key: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "mcp_api_key", default=None
)
