"""photoram-cli CLI — modern photo tagger powered by RAM++.

Exit codes:
    0 — success
    1 — no images found
    2 — invalid arguments (threshold, top-n, device, etc.)
    3 — model error (download, corruption, inference)
    4 — other runtime error
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import os
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

from . import __version__
from .errors import (
    EXIT_INVALID_ARGS,
    EXIT_NO_IMAGES,
    EXIT_SUCCESS,
    MetadataWriteError,
    NoImagesError,
    PhotoramError,
    ValidationError,
)
from .metadata import write_metadata
from .schemas import BatchResult
from .service import TaggingService
from .utils import format_tags_text


def _is_utf8_capable() -> bool:
    """Check if stderr supports UTF-8 output."""
    try:
        encoding = getattr(sys.stderr, "encoding", None) or ""
        return "utf" in encoding.lower()
    except Exception:
        return False


# Force safe box-drawing and no colour when the terminal can't handle it
_SAFE = not _is_utf8_capable()
console = Console(
    stderr=True,
    safe_box=_SAFE,
    no_color=not sys.stderr.isatty(),
)

# Pick an ASCII-safe spinner when the terminal lacks UTF-8
_SPINNER = "line" if _SAFE else "dots"


# ---------------------------------------------------------------------------
# Click parameter validation callbacks
# ---------------------------------------------------------------------------

def _validate_threshold(ctx: click.Context, param: click.Parameter, value: float) -> float:
    if not 0.0 <= value <= 1.0:
        raise click.BadParameter(
            f"Must be between 0.0 and 1.0, got {value}.",
            param_hint="'--threshold'",
        )
    return value


def _validate_top_n(ctx: click.Context, param: click.Parameter, value: Optional[int]) -> Optional[int]:
    if value is not None and value < 1:
        raise click.BadParameter(
            f"Must be a positive integer, got {value}.",
            param_hint="'--top-n'",
        )
    return value


def _validate_batch_size(ctx: click.Context, param: click.Parameter, value: int) -> int:
    if value < 1:
        raise click.BadParameter(
            f"Must be a positive integer, got {value}.",
            param_hint="'--batch-size'",
        )
    return value


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group()
@click.version_option(__version__, prog_name="photoram-cli")
def main() -> None:
    """photoram-cli — Modern CLI photo tagger powered by RAM++."""


# ---------------------------------------------------------------------------
# tag command
# ---------------------------------------------------------------------------

@main.command()
@click.argument("input_paths", nargs=-1, required=False, metavar="INPUT...")
@click.option("-t", "--threshold", type=float, default=0.80, show_default=True,
              callback=_validate_threshold, expose_value=True, is_eager=True,
              help="Detection threshold (0.0–1.0).")
@click.option("-n", "--top-n", type=int, default=10,
              callback=_validate_top_n,
              help="Maximum number of tags to return.")
@click.option("-c", "--confidence", is_flag=True, default=False,
              help="Show confidence scores.")
@click.option("-f", "--format", "fmt", type=click.Choice(["text", "json", "csv"]),
              default="json", show_default=True, help="Output format.")
@click.option("-o", "--output", type=click.Path(), default=None,
              help="Write results to file instead of stdout.")
@click.option("-r", "--recursive", is_flag=True, default=True,
              help="Recursively scan directories.")
@click.option("-w", "--write-metadata", "write_meta", is_flag=True, default=False,
              help="Write tags to image EXIF/XMP/IPTC metadata.")
@click.option("--overrides", type=click.Path(exists=True), default=None,
              help="Tag override/translation JSON file.")
@click.option("--device", type=str, default=None,
              help="Force device: cpu, cuda, mps (default: auto).")
@click.option("--image-size", type=int, default=512, show_default=True,
              help="Input image size for the model.")
@click.option("--batch-size", type=int, default=32, show_default=True,
              callback=_validate_batch_size,
              help="Images per inference batch (higher = faster on GPU, more VRAM).")
@click.option("--chinese", is_flag=False, default=False,
              help="Also output Chinese tags.")
@click.option("-T", "--timings", is_flag=True, default=True,
              help="Print basic timings (load, tagging, total).")
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
    batch_size: int,
    chinese: bool,
    timings: bool,
    quiet: bool,
    # compat
    compat_image: Optional[str],
    compat_output: Optional[str],
    compat_conf: bool,
) -> None:
    """Tag one or more images using RAM++.

    INPUT can be image files or directories.

    \b
    Exit codes:
      0  success
      1  no images found
      2  invalid arguments
      3  model error
    """
    # ---- photils-cli compatibility layer ----
    if compat_image:
        input_paths = (compat_image, *input_paths)
    if compat_output and not output:
        output = compat_output
    if compat_conf:
        confidence = True
    if not input_paths:
        raise click.UsageError("Missing argument 'INPUT...'.")

    total_start = time.perf_counter()

    # ---- Build service ----
    try:
        svc = TaggingService(
            threshold=threshold,
            device=device,
            image_size=image_size,
            top_n=top_n,
            overrides=overrides,
            batch_size=batch_size,
        )
    except ValidationError as e:
        console.print(f"[red]Validation error:[/red] {e}")
        raise SystemExit(EXIT_INVALID_ARGS)

    # ---- Print config (unless quiet) ----
    if not quiet:
        console.print(
            "[dim]Device:[/dim] auto-detect" if device is None else f"[dim]Device:[/dim] {device}"
        )
        console.print(f"[dim]Threshold:[/dim] {threshold}")
        if batch_size > 1:
            console.print(f"[dim]Batch size:[/dim] {batch_size}")
        console.print()

    # ---- Load model ----
    try:
        with (
            console.status("Loading RAM++ model...", spinner=_SPINNER)
            if not quiet
            else _nullcontext()
        ):
            # Suppress RAM model's stdout prints ("load checkpoint from...",
            # "vit: swin_l") that would contaminate piped output.
            with _suppress_stdout():
                load_time = svc.load_model()
    except PhotoramError as e:
        console.print(f"[red]Model error:[/red] {e}")
        raise SystemExit(e.exit_code)

    if not quiet:
        console.print(
            f"[dim]Model loaded in {load_time:.1f}s on "
            f"[bold]{svc.resolved_device}[/bold][/dim]\n"
        )

    # ---- Collect & tag images ----
    progress_ctx = Progress(
        SpinnerColumn(spinner_name=_SPINNER),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green"),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
        disable=quiet,
    )

    try:
        tag_start = time.perf_counter()
        with progress_ctx as progress:
            task_id = progress.add_task("Tagging", total=0)

            def _on_progress(img_path: Path, current: int, total: int) -> None:
                progress.update(task_id, total=total, completed=current,
                                description=f"[cyan]{img_path.name}[/cyan]")

            batch = svc.tag_paths(
                input_paths,
                recursive=recursive,
                on_progress=_on_progress,
            )
        tag_time = time.perf_counter() - tag_start
    except NoImagesError as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(EXIT_NO_IMAGES)
    except PhotoramError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(e.exit_code)

    # ---- Write metadata if requested ----
    if write_meta:
        for result in batch.succeeded:
            try:
                write_metadata(result.path, result.tags)
            except MetadataWriteError as e:
                console.print(f"[yellow]Metadata warning:[/yellow] {e}")

    # ---- Report per-image errors ----
    for result in batch.failed:
        console.print(f"[red]Error processing {result.path}:[/red] {result.error}")

    # ---- Output ----
    _output_results(batch, fmt, confidence, chinese, output, quiet)

    if timings:
        total_time = time.perf_counter() - total_start
        num_images = len(batch.results)
        total_mp = sum(r.image_megapixels or 0 for r in batch.results)
        avg_megapixels = total_mp / num_images if num_images > 0 else 0
        _print_timings(
            load_time=load_time,
            tag_time=tag_time,
            total_time=total_time,
            num_images=num_images,
            avg_megapixels=avg_megapixels,
        )

    raise SystemExit(EXIT_SUCCESS)


# ---------------------------------------------------------------------------
# Output dispatcher
# ---------------------------------------------------------------------------

def _output_results(
    batch: BatchResult,
    fmt: str,
    show_confidence: bool,
    show_chinese: bool,
    output_path: Optional[str],
    quiet: bool,
) -> None:
    """Write results in the chosen format.

    JSON contract: **always a list**, even for a single image.
    """
    results = batch.results
    buf = io.StringIO()

    if fmt == "json":
        # Stable contract: always a JSON array
        data = batch.to_list(
            include_chinese=show_chinese,
            include_confidences=show_confidence,
        )
        json.dump(data, buf, indent=2, ensure_ascii=False)
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
            row: list[str] = [r.path, " | ".join(r.tags)]
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


def _print_timings(
    load_time: float,
    tag_time: float,
    total_time: float,
    num_images: int,
    avg_megapixels: float,
) -> None:
    """Print a compact timing summary to stderr."""
    console.print("[dim]Timings:[/dim]")
    console.print(f"[dim]  model load:[/dim] {load_time:.3f}s")
    console.print(f"[dim]  tagging:[/dim] {tag_time:.3f}s")
    console.print(f"[dim]  total:[/dim] {total_time:.3f}s")
    console.print(f"[dim]  images:[/dim] {num_images}")
    if avg_megapixels > 0:
        console.print(f"[dim]  avg megapixels:[/dim] {avg_megapixels:.1f} MP")


@contextlib.contextmanager
def _suppress_stdout():
    """Redirect stdout to devnull to suppress noisy library prints.

    The RAM package prints 'load checkpoint from ...' and 'vit: swin_l'
    directly to stdout during model loading, which contaminates piped
    JSON/CSV output.  This silences those prints.
    """
    old_fd = os.dup(1)
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 1)
        os.close(devnull)
        yield
    finally:
        os.dup2(old_fd, 1)
        os.close(old_fd)


# ---------------------------------------------------------------------------
# photils-cli compat: `photoram-cli --image X` at top level
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

    console.print(f"[bold]photoram-cli[/bold] v{__version__}")
    console.print(f"  PyTorch: {torch.__version__}")
    console.print(f"  CUDA available: {torch.cuda.is_available()}")
    if hasattr(torch.backends, "mps"):
        console.print(f"  MPS available: {torch.backends.mps.is_available()}")

    from .model import RAMPlusModel
    console.print(f"  Default device: {RAMPlusModel._resolve_device(device)}")

    from .model import CACHE_DIR, HF_FILENAME
    ckpt = CACHE_DIR / HF_FILENAME
    console.print(f"  Model cached: {ckpt.exists()}")
    if ckpt.exists():
        size_mb = ckpt.stat().st_size / (1024 * 1024)
        console.print(f"  Model size: {size_mb:.0f} MB")
        console.print(f"  Model path: {ckpt}")
