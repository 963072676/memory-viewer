"""Memory Viewer CLI - Main entry point.

Commands: import, export, search, list, tag, archive, delete, stats, digest, config.
"""

import json
import os
import sys
from pathlib import Path

import click
import httpx
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich import print as rprint

console = Console()

CONFIG_PATH = Path.home() / ".mv-cli" / "config.json"

DEFAULT_CONFIG = {
    "base_url": "http://localhost:8000",
    "api_key": "",
    "output_format": "table",
}


def load_config() -> dict:
    """Load CLI config from ~/.mv-cli/config.json."""
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """Save CLI config."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))


def get_client() -> httpx.Client:
    """Get configured HTTP client."""
    config = load_config()
    headers = {"Content-Type": "application/json"}
    if config.get("api_key"):
        headers["X-Api-Key"] = config["api_key"]
    return httpx.Client(base_url=config["base_url"], headers=headers, timeout=30)


def api_get(path: str, params: dict = None) -> dict:
    """Make GET request."""
    with get_client() as client:
        resp = client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()


def api_post(path: str, data: dict = None) -> dict:
    """Make POST request."""
    with get_client() as client:
        resp = client.post(path, json=data or {})
        resp.raise_for_status()
        return resp.json()


def api_put(path: str, data: dict = None) -> dict:
    """Make PUT request."""
    with get_client() as client:
        resp = client.put(path, json=data or {})
        resp.raise_for_status()
        return resp.json()


def api_delete(path: str) -> dict:
    """Make DELETE request."""
    with get_client() as client:
        resp = client.delete(path)
        resp.raise_for_status()
        return resp.json()


@click.group()
@click.version_option(version="2.2.0")
def cli():
    """Memory Viewer CLI — Bulk operations for memory management."""
    pass


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["json", "markdown"]), default="json")
def import_cmd(file: str, fmt: str):
    """Import memories from a file."""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TaskProgressColumn(), console=console) as progress:
        task = progress.add_task("Importing memories...", total=None)
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        # Use multipart for file import
        config = load_config()
        with httpx.Client(base_url=config["base_url"], timeout=60) as client:
            files = {"file": (os.path.basename(file), content, "application/json" if fmt == "json" else "text/markdown")}
            resp = client.post("/api/agentmemory/import", files=files)
            resp.raise_for_status()
            result = resp.json()
        progress.update(task, completed=1)
    console.print(f"[green]✓[/] Imported: {result.get('imported', 0)}, Skipped: {result.get('skipped', 0)}, Failed: {result.get('failed', 0)}")


@cli.command()
@click.option("--format", "fmt", type=click.Choice(["json", "markdown"]), default="json")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--ids", help="Comma-separated memory IDs to export")
def export(fmt: str, output: str, ids: str):
    """Export memories to file."""
    params = {"format": fmt}
    if ids:
        params["ids"] = ids
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Exporting memories...", total=None)
        config = load_config()
        with httpx.Client(base_url=config["base_url"], timeout=60) as client:
            resp = client.get("/api/agentmemory/export", params=params)
            resp.raise_for_status()
            content = resp.text
        progress.update(task, completed=1)
    if output:
        Path(output).write_text(content, encoding="utf-8")
        console.print(f"[green]✓[/] Exported to {output}")
    else:
        click.echo(content)


@cli.command()
@click.argument("query")
@click.option("--limit", "-n", default=10)
@click.option("--mode", type=click.Choice(["keyword", "semantic", "rag"]), default="keyword")
def search(query: str, limit: int, mode: str):
    """Search memories."""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task(f"Searching ({mode})...", total=None)
        if mode == "rag":
            result = api_post("/api/search/rag", {"query": query, "top_k": limit})
        elif mode == "semantic":
            result = api_get(f"/api/search/semantic", {"q": query, "limit": limit, "mode": "semantic"})
        else:
            result = api_get("/api/search", {"q": query, "limit": limit})
        progress.update(task, completed=1)

    if mode == "rag":
        console.print(Panel(result.get("answer", ""), title="🤖 AI Answer", border_style="blue"))
        console.print(f"Confidence: {result.get('confidence', 0):.0%}")
        if result.get("sources"):
            table = Table(title="Sources")
            table.add_column("#", style="dim")
            table.add_column("Title")
            table.add_column("Similarity")
            for i, src in enumerate(result["sources"], 1):
                table.add_row(str(i), src.get("title", ""), f"{src.get('similarity', 0)}%")
            console.print(table)
    else:
        results = result.get("results", result.get("memories", []))
        if not results:
            console.print("[yellow]No results found.[/]")
            return
        table = Table(title=f"Search Results ({len(results)})")
        table.add_column("ID", style="dim", max_width=20)
        table.add_column("Title")
        table.add_column("Type")
        table.add_column("Score")
        for r in results:
            score = r.get("similarity", r.get("score", ""))
            table.add_row(r.get("id", "")[:16], r.get("title", ""), r.get("type", ""), str(score))
        console.print(table)


@cli.command("list")
@click.option("--limit", "-n", default=20)
@click.option("--offset", default=0)
@click.option("--type", "mem_type", help="Filter by type")
@click.option("--tag", help="Filter by tag")
@click.option("--archived", is_flag=True, help="Show archived only")
def list_cmd(limit: int, offset: int, mem_type: str, tag: str, archived: bool):
    """List memories."""
    params = {"limit": limit, "offset": offset}
    if mem_type:
        params["type"] = mem_type
    if tag:
        params["tag"] = tag
    if archived:
        params["archived"] = "true"
    result = api_get("/api/agentmemory/paginated", params)
    memories = result.get("memories", [])
    total = result.get("total", 0)
    table = Table(title=f"Memories ({total} total, showing {offset+1}-{offset+len(memories)})")
    table.add_column("ID", style="dim", max_width=16)
    table.add_column("Title", max_width=40)
    table.add_column("Type")
    table.add_column("Strength")
    table.add_column("Tags")
    for m in memories:
        tags = ", ".join(m.get("tags", [])[:3])
        table.add_row(m.get("id", "")[:14], m.get("title", ""), m.get("type", ""), str(m.get("strength", "")), tags)
    console.print(table)


@cli.command()
@click.argument("ids", nargs=-1, required=True)
@click.argument("tags_to_add", nargs=-1)
@click.option("--add", "add_tags", multiple=True, help="Tags to add")
@click.option("--remove", "remove_tags", multiple=True, help="Tags to remove")
def tag(ids: tuple, add_tags: tuple, remove_tags: tuple):
    """Add/remove tags from memories."""
    id_list = list(ids)
    if add_tags:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(f"Tagging {len(id_list)} memories...", total=None)
            result = api_post("/api/memories/batch-add-tags", {"ids": id_list, "tags": list(add_tags)})
            progress.update(task, completed=1)
        console.print(f"[green]✓[/] Tagged {result.get('processed', 0)} memories")


@cli.command()
@click.argument("ids", nargs=-1, required=True)
def archive(ids: tuple):
    """Archive memories."""
    id_list = list(ids)
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task(f"Archiving {len(id_list)} memories...", total=None)
        result = api_post("/api/agentmemory/batch/archive", {"ids": id_list})
        progress.update(task, completed=1)
    console.print(f"[green]✓[/] Archived {result.get('processed', 0)} memories")


@cli.command()
@click.argument("ids", nargs=-1, required=True)
@click.option("--confirm", is_flag=True, help="Skip confirmation")
def delete(ids: tuple, confirm: bool):
    """Delete memories."""
    id_list = list(ids)
    if not confirm:
        click.confirm(f"Delete {len(id_list)} memories?", abort=True)
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task(f"Deleting {len(id_list)} memories...", total=None)
        result = api_post("/api/agentmemory/batch/delete", {"ids": id_list})
        progress.update(task, completed=1)
    console.print(f"[green]✓[/] Deleted {result.get('deleted', 0)} memories")


@cli.command()
def stats():
    """Show memory statistics."""
    result = api_get("/api/stats")
    table = Table(title="Memory Statistics")
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    for key, value in result.items():
        if isinstance(value, (str, int, float)):
            table.add_row(key, str(value))
    console.print(table)


@cli.command()
@click.option("--type", "digest_type", type=click.Choice(["daily", "weekly", "custom"]), default="daily")
@click.option("--start", help="Start date (YYYY-MM-DD) for custom range")
@click.option("--end", help="End date (YYYY-MM-DD) for custom range")
def digest(digest_type: str, start: str, end: str):
    """Generate a memory digest."""
    body: dict = {"type": digest_type}
    if digest_type == "custom":
        body["start_date"] = start
        body["end_date"] = end
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Generating digest...", total=None)
        result = api_post("/api/digest/generate", body)
        progress.update(task, completed=1)
    d = result.get("digest", {})
    console.print(Panel(d.get("summary", ""), title=f"📋 {digest_type.title()} Digest", border_style="blue"))
    sections = d.get("sections", {})
    if sections.get("new_memories"):
        console.print(f"\n[bold]🆕 New Memories:[/] {len(sections['new_memories'])}")
    if sections.get("health_alerts"):
        console.print(f"[bold red]⚠️ Health Alerts:[/] {len(sections['health_alerts'])}")


@cli.command()
@click.option("--set", "set_value", nargs=2, type=str, help="Set config value (key value)")
@click.option("--get", "get_key", help="Get config value")
@click.option("--list", "list_config", is_flag=True, help="Show all config")
def config(set_value: tuple, get_key: str, list_config: bool):
    """Manage CLI configuration."""
    cfg = load_config()
    if set_value:
        key, value = set_value
        if key == "base_url":
            cfg["base_url"] = value.rstrip("/")
        elif key == "api_key":
            cfg["api_key"] = value
        elif key == "output_format":
            cfg["output_format"] = value
        else:
            cfg[key] = value
        save_config(cfg)
        console.print(f"[green]✓[/] Set {key} = {value}")
    elif get_key:
        console.print(f"{get_key} = {cfg.get(get_key, 'not set')}")
    else:
        table = Table(title="CLI Configuration")
        table.add_column("Key", style="bold")
        table.add_column("Value")
        for k, v in cfg.items():
            display_v = "***" if k == "api_key" and v else str(v)
            table.add_row(k, display_v)
        console.print(table)
        console.print(f"\nConfig path: {CONFIG_PATH}")


# Alias import command
cli.add_command(import_cmd, name="import")

if __name__ == "__main__":
    cli()
