"""``vlens`` CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from .config.loader import load_config
from .publish.artifacts import write_bundle
from .publish.jsonschema_export import export as export_schemas
from .publish.manifest import verify_bundle as _verify_bundle
from .publish.upload_vercel import upload_bundle
from .utils.logging import get_logger
from .utils.seeding import set_global_seed

app = typer.Typer(no_args_is_help=True, add_completion=False)
schema_app = typer.Typer(no_args_is_help=True)
publish_app = typer.Typer(no_args_is_help=True)
app.add_typer(schema_app, name="schema")
app.add_typer(publish_app, name="publish-cmd", hidden=True)  # alias path


LOG = get_logger("vlens.cli")


@app.command("publish")
def publish(
    config: Annotated[Path, typer.Option("--config", help="Path to YAML config")],
    out: Annotated[Path, typer.Option("--out", help="Output bundle root directory")],
) -> None:
    """Run the pipeline and write a signed artifact bundle."""
    cfg = load_config(config)
    set_global_seed(cfg.seed)
    write_bundle(out_root=out, cfg=cfg)
    typer.echo(f"bundle written to {out}")


@app.command("upload")
def upload(bundle: Annotated[Path, typer.Option("--bundle")]) -> None:
    """Upload a bundle (no-op without Vercel Blob env vars)."""
    url = upload_bundle(bundle)
    typer.echo(url)


@app.command("verify")
def verify(bundle: Annotated[Path, typer.Option("--bundle")]) -> None:
    """Verify a bundle's manifest signature + schema_version."""
    manifest = _verify_bundle(bundle)
    typer.echo(f"OK bundle_id={manifest['bundle_id']} schema_version={manifest['schema_version']}")


@schema_app.command("export")
def schema_export(
    out: Annotated[Path, typer.Option("--out", help="Output JSON Schema file")],
) -> None:
    """Export pydantic models to a single JSON Schema bundle."""
    p = export_schemas(out)
    typer.echo(f"schemas written to {p}")


if __name__ == "__main__":  # pragma: no cover
    app()
