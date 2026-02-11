"""photoram CLI — modern photo tagger powered by RAM++."""

from __future__ import annotations

import csv
import io
import json
import sys
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from . import __version__
from .metadata import write_metadata
from .model import RAMPlusModel, TagResult
from .utils import (
    apply_overrides,
    collect_images,
    format_result_json,
    format_tags_text,
    load_overrides,
)

console = Console(stderr=True)


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group()
@click.version_option(__version__, prog_name="photoram")
def main() -> None:
    """photoram — Modern CLI photo tagger powered by RAM++."""


# ---------------------------------------------------------------------------
# tag command
# ---------------------------------------------------------------------------

@main.command()
@click.argument("input_paths", nargs=-1, required=True, metavar="INPUT...")
@click.option("-t", "--threshold", type=float, default=0.5, show_default=True,
              help="Detection threshold (0.0–1.0).")
@click.option("-n", "--top-n", type=int, default=None,
              help="Maximum number of tags to return.")
@click.option("-c", "--confidence", is_flag=True, default=False,
              help="Show confidence scores.")
@click.option("-f", "--format", "fmt", type=click.Choice(["text", "json", "csv"]),
              default="text", show_default=True, help="Output format.")
@click.option("-o", "--output", type=click.Path(), default=None,
              help="Write results to file instead of stdout.")
@click.option("-r", "--recursive", is_flag=True, default=False,
              help="Recursively scan directories.")
@click.option("-w", "--write-metadata", "write_meta", is_flag=True, default=False,
              help="Write tags to image EXIF/XMP/IPTC metadata.")
@click.option("--overrides", type=click.Path(exists=True), default=None,
              help="Tag override/translation JSON file.")
@click.option("--device", type=str, default=None,
              help="Force device: cpu, cuda, mps (default: auto).")
@click.option("--image-size", type=int, default=384, show_default=True,
              help="Input image size for the model.")
@click.option("--chinese", is_flag=True, default=False,
              help="Also output Chinese tags.")
@click.option("-q", "--quiet", is_flag=True, default=False,
              help="Suppress progress output.")
# photils-cli compat aliases
@click.option("-i", "--image", "compat_image", type=click.Path(), default=None,
              hidden=True, help="photils-cli compat: same as positional INPUT.")
@click.option("--output_file", "compat_output", type=click.Path(), default=None,
              hidden=True, help="photils-cli compat: same as --output.")
@click.option("--with_confidence", "compat_conf", is_flag=True, default=False,
              hidden=True, help="photils-cli compat: same as --confidence.")
def tag(
    input_paths: tuple[str, ...],
    threshold: float,
    top_n: Optional[int],
    confidence: bool,
    fmt: str,
    output: Optional[str],
    recursive: bool,
    write_meta: bool,
    overrides: Optional[str],
    device: Optional[str],
    image_size: int,
    chinese: bool,
    quiet: bool,
    # compat
    compat_image: Optional[str],
    compat_output: Optional[str],
    compat_conf: bool,
) -> None:
    """Tag one or more images using RAM++.

    INPUT can be image files or directories.
    """
    # ---- photils-cli compatibility layer ----
    if compat_image:
        input_paths = (compat_image, *input_paths)
    if compat_output and not output:
        output = compat_output
    if compat_conf:
        confidence = True

    # ---- Collect images ----
    images = collect_images(input_paths, recursive=recursive)
    if not images:
        console.print("[red]No images found.[/red]")
        raise SystemExit(1)

    # ---- Load tag overrides ----
    override_map = load_overrides(overrides)

    # ---- Load model ----
    if not quiet:
        console.print(f"[dim]Device:[/dim] auto-detect" if device is None else f"[dim]Device:[/dim] {device}")
        console.print(f"[dim]Threshold:[/dim] {threshold}")
        console.print(f"[dim]Images:[/dim] {len(images)}")
        console.print()

    with console.status("[bold green]Loading RAM++ model…[/bold green]", spinner="dots") if not quiet else _nullcontext():
        t0 = time.time()
        ram_model = RAMPlusModel(
            device=device,
            image_size=image_size,
            threshold=threshold,
        )
        # Force model load now
        _ = ram_model.model
        load_time = time.time() - t0

    if not quiet:
        console.print(f"[dim]Model loaded in {load_time:.1f}s on [bold]{ram_model.device}[/bold][/dim]\n")

    # ---- Process images ----
    results: list[TagResult] = []

    progress_ctx = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
        disable=quiet,
    )

    with progress_ctx as progress:
        task_id = progress.add_task("Tagging", total=len(images))
        for img_path in images:
            progress.update(task_id, description=f"[cyan]{img_path.name}[/cyan]")
            try:
                result = ram_model.tag_image(img_path)

                # Apply overrides
                result.tags = apply_overrides(result.tags, override_map)

                # Limit tags
                if top_n:
                    result.tags = result.tags[:top_n]
                    result.tags_chinese = result.tags_chinese[:top_n]
                    result.confidences = result.confidences[:top_n]

                results.append(result)

                # Write metadata if requested
                if write_meta:
                    try:
                        write_metadata(img_path, result.tags)
                    except RuntimeError as e:
                        console.print(f"[yellow]Warning:[/yellow] {e}")

            except Exception as e:
                console.print(f"[red]Error processing {img_path}:[/red] {e}")

            progress.advance(task_id)

    # ---- Output ----
    _output_results(results, fmt, confidence, chinese, output, quiet)


# ---------------------------------------------------------------------------
# Output dispatcher
# ---------------------------------------------------------------------------

def _output_results(
    results: list[TagResult],
    fmt: str,
    show_confidence: bool,
    show_chinese: bool,
    output_path: Optional[str],
    quiet: bool,
) -> None:
    """Write results in the chosen format."""
    buf = io.StringIO()

    if fmt == "json":
        data = [
            format_result_json(
                r.path, r.tags, r.confidences,
                r.tags_chinese if show_chinese else None,
            )
            for r in results
        ]
        json.dump(data if len(data) > 1 else data[0], buf, indent=2, ensure_ascii=False)
        buf.write("\n")

    elif fmt == "csv":
        writer = csv.writer(buf)
        header = ["file", "tags"]
        if show_confidence:
            header.append("confidences")
        if show_chinese:
            header.append("tags_chinese")
        writer.writerow(header)
        for r in results:
            row = [r.path, " | ".join(r.tags)]
            if show_confidence:
                row.append(" | ".join(f"{c:.4f}" for c in r.confidences))
            if show_chinese:
                row.append(" | ".join(r.tags_chinese))
            writer.writerow(row)

    else:  # text
        if len(results) == 1:
            # Single-image: just print tags (photils-cli compatible)
            r = results[0]
            buf.write(format_tags_text(r.tags, r.confidences, show_confidence))
            buf.write("\n")
            if show_chinese:
                buf.write(format_tags_text(r.tags_chinese))
                buf.write("\n")
        else:
            # Multi-image: table-like output
            for r in results:
                buf.write(f"{r.path}\t")
                buf.write(format_tags_text(r.tags, r.confidences, show_confidence))
                buf.write("\n")
                if show_chinese:
                    buf.write(f"{r.path}\t")
                    buf.write(format_tags_text(r.tags_chinese))
                    buf.write("\n")

    text = buf.getvalue()

    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
        if not quiet:
            console.print(f"[green]Results written to {output_path}[/green]")
    else:
        sys.stdout.write(text)


# ---------------------------------------------------------------------------
# Rich-compatible null context manager
# ---------------------------------------------------------------------------

class _nullcontext:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


# ---------------------------------------------------------------------------
# photils-cli compat: `photoram --image X` at top level
# ---------------------------------------------------------------------------

@main.command(hidden=True, name="compat-tag")
@click.pass_context
def _compat_tag(ctx: click.Context) -> None:
    """Hidden compat entry for photils-cli style invocation."""
    ctx.invoke(tag)


# ---------------------------------------------------------------------------
# info command
# ---------------------------------------------------------------------------

@main.command()
@click.option("--device", type=str, default=None)
def info(device: Optional[str]) -> None:
    """Show model and environment info."""
    import torch

    console.print(f"[bold]photoram[/bold] v{__version__}")
    console.print(f"  PyTorch: {torch.__version__}")
    console.print(f"  CUDA available: {torch.cuda.is_available()}")
    if hasattr(torch.backends, "mps"):
        console.print(f"  MPS available: {torch.backends.mps.is_available()}")
    console.print(f"  Default device: {RAMPlusModel._resolve_device(device)}")

    from .model import CACHE_DIR, HF_FILENAME
    ckpt = CACHE_DIR / HF_FILENAME
    console.print(f"  Model cached: {ckpt.exists()}")
    if ckpt.exists():
        size_mb = ckpt.stat().st_size / (1024 * 1024)
        console.print(f"  Model size: {size_mb:.0f} MB")
        console.print(f"  Model path: {ckpt}")
