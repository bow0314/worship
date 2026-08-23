#!/usr/bin/env python3
"""Render a PDF's pages to PNG so they can be read visually.

Worship lyric-sheet PDFs from Google Drive are almost always scanned
images with no text layer, so pypdf/pdfplumber text extraction comes
back empty. Rendering each page to an image and reading it with Claude's
vision (the Read tool) is the reliable path — this script does the
rendering step.

Handles two input shapes:
1. A raw .pdf file path.
2. A JSON file saved by the Google Drive `download_file_content` MCP
   tool. When the decoded content is too large to inline, the tool
   writes it to a tool-results file instead and that file has the shape
   {"content": "<base64 pdf bytes>", "id": ..., "mimeType": ..., "title": ...}.
   This script detects that shape automatically from the .json extension.

Usage:
    python render_pdf_pages.py <input.pdf|input.json> <output_dir> [--scale 2.5]

Prints one image path per line on stdout, in page order, so the caller
can feed them straight into Read calls.
"""
import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path


def ensure_pypdfium2():
    try:
        import pypdfium2  # noqa: F401
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "pypdfium2"],
            check=True,
        )


def load_pdf_bytes(input_path: Path) -> bytes:
    if input_path.suffix.lower() == ".pdf":
        return input_path.read_bytes()

    data = json.loads(input_path.read_text())
    content = data.get("content")
    if content is None:
        raise ValueError(
            f"No 'content' field in {input_path} — expected the JSON shape "
            "saved by the Google Drive download_file_content tool "
            '({"content": "<base64>", ...}). Pass the .pdf directly if you '
            "already have raw PDF bytes on disk."
        )
    return base64.b64decode(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Path to a .pdf, or a .json saved by download_file_content")
    parser.add_argument("output_dir", help="Directory to write page_N.png files into")
    parser.add_argument(
        "--scale",
        type=float,
        default=2.5,
        help="Render scale. 2.5 keeps dense lyric-sheet text legible without huge files.",
    )
    args = parser.parse_args()

    ensure_pypdfium2()
    import pypdfium2 as pdfium

    input_path = Path(args.input)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf = pdfium.PdfDocument(load_pdf_bytes(input_path))
    for i in range(len(pdf)):
        image = pdf[i].render(scale=args.scale).to_pil()
        out_path = out_dir / f"page_{i + 1}.png"
        image.save(out_path)
        print(out_path)


if __name__ == "__main__":
    main()
