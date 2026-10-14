"""Minimal MCP Streamable-HTTP client (no third-party deps).

Token comes from the MCD_MCP_TOKEN environment variable -- never hardcode it,
never commit it. Get one at https://open.mcd.cn (console -> activate).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error

ENDPOINT = "https://mcp.mcd.cn"


def _token() -> str:
    tok = os.environ.get("MCD_MCP_TOKEN", "").strip()
    if not tok:
        sys.exit("error: set MCD_MCP_TOKEN env var (your McDonald's MCP Token from open.mcd.cn)")
    return tok


def _post(payload: dict, session_id: str | None = None):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {_token()}",
        },
    )
    if session_id:
        req.add_header("Mcp-Session-Id", session_id)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            new_session = resp.headers.get("Mcp-Session-Id") or session_id
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        sys.exit(f"error: HTTP {exc.code} {exc.reason} {detail}")
    text = raw.decode("utf-8", "replace")
    if not text.strip():
        return None, new_session  # 202 Accepted, normal for notifications
    ctype = ""
    try:
        ctype = resp.headers.get("Content-Type", "")
    except Exception:
        pass
    if "text/event-stream" in ctype:
        msgs = [json.loads(l[5:].strip()) for l in text.splitlines()
                if l.strip().startswith("data:") and l[5:].strip() not in ("", "[DONE]")]
        return (msgs[0] if len(msgs) == 1 else msgs), new_session
    return json.loads(text), new_session


class Session:
    def __init__(self):
        self.sid = None
        self._id = 0
        self._ready = False

    def _rpc(self, method, params=None, notify=False):
        self._id += 1
        msg = {"jsonrpc": "2.0", "method": method}
        if not notify:
            msg["id"] = self._id
        if params is not None:
            msg["params"] = params
        parsed, self.sid = _post(msg, self.sid)
        if notify or parsed is None:
            return None
        if isinstance(parsed, dict) and "error" in parsed:
            sys.exit(f"error: {parsed['error'].get('message')}")
        return parsed

    def ensure(self):
        if self._ready:
            return
        self._rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                                 "clientInfo": {"name": "macnomics", "version": "0.1"}})
        self._rpc("notifications/initialized", notify=True)
        self._ready = True

    def call(self, tool: str, args: dict) -> dict:
        self.ensure()
        res = self._rpc("tools/call", {"name": tool, "arguments": args})
        return res.get("result", {})


def tool_call(tool: str, args: dict) -> dict:
    """One-shot tool call (fresh session each time)."""
    return Session().call(tool, args)


def structured(tool: str, args: dict):
    """Return the structuredContent payload of a tool call."""
    res = tool_call(tool, args)
    return res.get("structuredContent", {})
