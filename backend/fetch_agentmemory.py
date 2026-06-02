#!/usr/bin/env python3
"""
T3-DEV-02 (adapted for container): agentmemory data export script.

Calls MCP server via stdio JSON-RPC to export agentmemory data to JSON cache.

Usage:
    python3 fetch_agentmemory.py [--output PATH]

Default output: ./cache/agentmemory.json (relative to script dir)
Env override: AGENTMEMORY_CACHE

Behavior:
    - On success: writes cache file
    - On failure: does NOT overwrite existing cache
    - Logs to stdout
"""

import argparse
import json
import os
import subprocess
import sys
import threading

APP_DIR = os.path.dirname(os.path.abspath(__file__))
# Default output must match settings.AGENTMEMORY_CACHE in app/config.py,
# which is _project_path("data", "cache", "agentmemory.json") = <repo>/data/cache/agentmemory.json.
# Writing anywhere else means the viewer will read stale data.
_REPO_ROOT = os.path.dirname(APP_DIR)
DEFAULT_OUTPUT = os.environ.get(
    "AGENTMEMORY_CACHE",
    os.path.join(_REPO_ROOT, "data", "cache", "agentmemory.json"),
)
TIMEOUT_SECONDS = 30

# Standalone JSON produced by @agentmemory/agentmemory when running in
# InMemoryKV / file-persist mode. Real persistent data lives here even when
# the MCP livez probe at :3111 is unreachable, so we always read it as the
# authoritative source and merge MCP export results on top.
STANDALONE_PATHS = [
    os.environ.get("AGENTMEMORY_STANDALONE", "").strip() or None,
    "/opt/data/.agentmemory/standalone.json",
    os.path.expanduser("~/.agentmemory/standalone.json"),
]


def resolve_mcp_bin() -> str:
    """Locate the @agentmemory/mcp bin.mjs across known npm cache locations.

    Hard-coded npx cache paths can vanish after container rebuilds or
    user-homedir migrations, so we probe the most common roots in order.
    Env override (AGENTMEMORY_MCP_BIN) wins so ops can pin a path explicitly.
    """
    override = os.environ.get("AGENTMEMORY_MCP_BIN")
    if override and os.path.isfile(override):
        return override

    candidates = []
    for root in ("/opt/data/.npm", "/home/.npm", "/root/.npm"):
        npx_dir = os.path.join(root, "_npx")
        if not os.path.isdir(npx_dir):
            continue
        for entry in sorted(os.listdir(npx_dir), reverse=True):
            candidate = os.path.join(
                npx_dir, entry, "node_modules", "@agentmemory", "mcp", "bin.mjs"
            )
            if os.path.isfile(candidate):
                candidates.append(candidate)

    if not candidates:
        raise RuntimeError(
            "Could not locate @agentmemory/mcp/bin.mjs under any known "
            "npm cache root. Set AGENTMEMORY_MCP_BIN to override."
        )
    return candidates[0]


def log(msg: str) -> None:
    print(f"[fetch_agentmemory] {msg}", flush=True)


def _load_standalone_memories() -> list[dict]:
    """Read the agentmemory standalone.json file (persistent storage).

    Schema: {"mem:memories": {<id>: {<memory fields>, ...}, ...}, "mem:sessions": {...}}
    Returns the memories list, with default version metadata filled in.
    """
    for path in STANDALONE_PATHS:
        if not path or not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            log(f"Standalone read failed at {path}: {e}")
            continue

        if not isinstance(raw, dict):
            log(f"Standalone {path}: top-level not a dict, skipping")
            continue

        bucket = raw.get("mem:memories")
        if not isinstance(bucket, dict):
            log(f"Standalone {path}: missing 'mem:memories' dict")
            continue

        out = []
        for mem_id, mem in bucket.items():
            if not isinstance(mem, dict):
                continue
            mem.setdefault("id", mem_id)
            mem.setdefault("version", "0.9.x")
            mem.setdefault("isLatest", True)
            out.append(mem)
        log(f"Loaded {len(out)} memories from standalone {path}")
        return out

    log("No standalone.json found in known locations")
    return []


def _merge_memories(*sources: list[dict]) -> list[dict]:
    """Merge multiple memory lists, dedup by id, keep the entry with the
    most recent updatedAt (falling back to createdAt)."""
    by_id: dict[str, dict] = {}
    for source in sources:
        for mem in source:
            mid = mem.get("id")
            if not mid:
                continue
            existing = by_id.get(mid)
            if not existing:
                by_id[mid] = mem
                continue
            new_ts = mem.get("updatedAt") or mem.get("createdAt") or ""
            old_ts = existing.get("updatedAt") or existing.get("createdAt") or ""
            if new_ts >= old_ts:
                by_id[mid] = mem
    return list(by_id.values())


def call_mcp_export() -> dict:
    """Start MCP server via stdio, call memory_export, return result dict."""
    log("Starting MCP server process...")

    proc = subprocess.Popen(
        ["node", resolve_mcp_bin()],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout_lines = []
    stderr_lines = []

    def read_stdout():
        for line in proc.stdout:
            stripped = line.strip()
            if stripped:
                stdout_lines.append(stripped)

    def read_stderr():
        for line in proc.stderr:
            stripped = line.strip()
            if stripped:
                stderr_lines.append(stripped)

    stdout_thread = threading.Thread(target=read_stdout, daemon=True)
    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
    stdout_thread.start()
    stderr_thread.start()

    try:
        messages = [
            json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "fetch_agentmemory", "version": "1.0.0"},
                },
            }),
            json.dumps({
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
            }),
            json.dumps({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "memory_export",
                    "arguments": {},
                },
            }),
        ]

        for msg in messages:
            proc.stdin.write(msg + "\n")
        proc.stdin.flush()
        proc.stdin.close()
        log("Sent initialize + memory_export requests")

        proc.wait(timeout=TIMEOUT_SECONDS)

        for line in stderr_lines:
            log(f"MCP stderr: {line}")

        if proc.returncode != 0:
            raise RuntimeError(
                f"MCP server exited with code {proc.returncode}: "
                + ("; ".join(stderr_lines[-3:]) if stderr_lines else "unknown error")
            )

        init_resp = None
        export_resp = None

        for line in stdout_lines:
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue
            resp_id = parsed.get("id")
            if resp_id == 1:
                init_resp = parsed
            elif resp_id == 2:
                export_resp = parsed

        if init_resp is None:
            raise RuntimeError("No initialize response received")
        if "error" in init_resp:
            raise RuntimeError(f"Initialize failed: {init_resp['error']}")
        log("MCP server initialized")

        if export_resp is None:
            raise RuntimeError("No memory_export response received")
        if "error" in export_resp:
            raise RuntimeError(f"memory_export failed: {export_resp['error']}")

        result = export_resp.get("result", {})
        content_list = result.get("content", [])

        if not content_list:
            raise RuntimeError("memory_export returned empty content")

        text_content = content_list[0].get("text", "{}")
        data = json.loads(text_content)
        log(f"Export successful: {len(data.get('memories', []))} memories retrieved")
        return data

    except subprocess.TimeoutExpired:
        proc.kill()
        raise RuntimeError(f"MCP server timed out after {TIMEOUT_SECONDS}s")
    except Exception:
        proc.kill()
        raise


def main():
    parser = argparse.ArgumentParser(description="Export agentmemory data to JSON cache")
    parser.add_argument(
        "--output", "-o",
        default=DEFAULT_OUTPUT,
        help=f"Output path (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()
    output_path = args.output

    log(f"Output path: {output_path}")

    existing_cache = os.path.exists(output_path)
    if existing_cache:
        log("Existing cache found — will only overwrite on success")

    try:
        return _run(output_path, existing_cache)
    except Exception as e:
        log(f"ERROR: {e}")
        if existing_cache:
            log("Preserving existing cache (no overwrite on failure)")
        else:
            log("No existing cache to preserve")
        return 1


def _run(output_path: str, existing_cache: bool) -> int:
    standalone = _load_standalone_memories()

    mcp_memories: list[dict] = []
    mcp_meta: dict = {}
    try:
        mcp_data = call_mcp_export()
        mcp_memories = mcp_data.get("memories", [])
        mcp_meta = {
            k: v for k, v in mcp_data.items() if k != "memories"
        }
    except Exception as e:
        log(f"MCP export failed (continuing with standalone only): {e}")

    merged = _merge_memories(standalone, mcp_memories)

    if not merged:
        raise RuntimeError(
            "No memories available from standalone.json or MCP export"
        )

    out = {
        "version": mcp_meta.get("version", "0.9.x"),
        "memories": merged,
    }
    sessions = mcp_meta.get("sessions")
    if sessions is not None:
        out["sessions"] = sessions

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    log(
        f"Cache written: {output_path} "
        f"(standalone={len(standalone)}, mcp={len(mcp_memories)}, "
        f"merged={len(merged)})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
