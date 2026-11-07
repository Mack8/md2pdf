#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["markdown"]
# ///
"""Convierte archivos Markdown a PDF, 100 % local y sin IA.

Uso:
    md2pdf documento.md                 # crea documento.pdf al lado
    md2pdf a.md b.md -o salida/         # varios archivos, carpeta de salida
    md2pdf carpeta/                     # todos los .md de la carpeta

Renderiza con el Edge/Chrome/Chromium que haya instalado (modo headless).
"""
import argparse
import html
import shutil
import subprocess
import sys
from pathlib import Path

import markdown

BROWSERS = [
    "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "/mnt/c/Program Files/Microsoft/Edge/Application/msedge.exe",
    "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
    "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
]
LINUX_BROWSERS = ["chromium", "chromium-browser", "google-chrome", "microsoft-edge"]

CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; line-height: 1.5; color: #1f2933; }
h1 { font-size: 20pt; border-bottom: 2px solid #2b6cb0; padding-bottom: 6px; color: #1a365d; }
h2 { font-size: 14.5pt; color: #2b6cb0; margin-top: 22px; border-bottom: 1px solid #cbd5e0; padding-bottom: 3px; page-break-after: avoid; }
h3 { font-size: 12pt; color: #2d3748; margin-top: 16px; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9.5pt; }
tr { page-break-inside: avoid; }
th { background: #edf2f7; text-align: left; }
th, td { border: 1px solid #cbd5e0; padding: 5px 8px; vertical-align: top; }
blockquote { margin: 10px 0; padding: 6px 14px; background: #fffaf0; border-left: 4px solid #dd6b20; }
code, pre { font-family: Consolas, monospace; background: #f7fafc; }
pre { padding: 10px; border: 1px solid #e2e8f0; white-space: pre-wrap; }
hr { border: 0; border-top: 1px solid #e2e8f0; margin: 18px 0; }
a { color: #2b6cb0; text-decoration: none; }
li { margin: 2px 0; }
"""


def find_browser() -> tuple[str, bool]:
    """Devuelve (ruta, es_windows)."""
    for path in BROWSERS:
        if Path(path).exists():
            return path, True
    for name in LINUX_BROWSERS:
        found = shutil.which(name)
        if found:
            return found, False
    sys.exit("No encontré Edge, Chrome ni Chromium. Instala uno de ellos.")


def wsl_path(path: Path, flag: str) -> str:
    return subprocess.run(["wslpath", flag, str(path)], capture_output=True, text=True, check=True).stdout.strip()


def render(md_file: Path, pdf_file: Path, browser: str, windows: bool) -> None:
    body = markdown.markdown(
        md_file.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
    )
    page = (
        f"<!doctype html><html lang='es'><head><meta charset='utf-8'>"
        f"<title>{html.escape(md_file.stem)}</title><style>{CSS}</style></head><body>{body}</body></html>"
    )
    # El HTML temporal va junto al PDF: Edge de Windows no lee bien /tmp de WSL.
    tmp_html = pdf_file.with_name(f".{pdf_file.stem}.tmp.html")
    tmp_html.write_text(page, encoding="utf-8")
    try:
        if windows:
            out_arg, url = wsl_path(pdf_file, "-w"), "file:///" + wsl_path(tmp_html, "-m")
        else:
            out_arg, url = str(pdf_file), tmp_html.resolve().as_uri()
        subprocess.run(
            [browser, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={out_arg}", url],
            capture_output=True, check=True, timeout=120,
        )
    finally:
        tmp_html.unlink(missing_ok=True)
    if not pdf_file.exists():
        sys.exit(f"El navegador no generó {pdf_file}")


def collect(inputs: list[str]) -> list[Path]:
    files: list[Path] = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            files += sorted(p.glob("*.md"))
        elif p.is_file():
            files.append(p)
        else:
            sys.exit(f"No existe: {item}")
    return files


def main() -> None:
    ap = argparse.ArgumentParser(description="Markdown a PDF, local y sin IA")
    ap.add_argument("entradas", nargs="+", help="archivos .md o carpetas")
    ap.add_argument("-o", "--out", help="carpeta de salida (por defecto junto al .md)")
    args = ap.parse_args()

    browser, windows = find_browser()
    for md_file in collect(args.entradas):
        out_dir = Path(args.out) if args.out else md_file.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        pdf_file = out_dir / f"{md_file.stem}.pdf"
        render(md_file, pdf_file, browser, windows)
        print(f"{md_file.name} -> {pdf_file}")


if __name__ == "__main__":
    main()
