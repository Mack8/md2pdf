# md2pdf

**English:** a tiny, single-file command-line tool that converts Markdown to PDF locally, with no AI and no cloud service. It renders the Markdown to HTML (with the `markdown` package) and prints it to PDF using whichever Microsoft Edge, Google Chrome or Chromium it finds, in headless mode. It targets Linux and WSL: on WSL it uses the Windows Edge or Chrome through `/mnt/c/...`, and on Linux it looks for `chromium`, `chromium-browser`, `google-chrome` or `microsoft-edge` in the `PATH`. macOS and native Windows are not supported yet.

**Español:** convierte archivos Markdown a PDF de forma local, sin IA y sin servicios en la nube.

## Uso / Usage

Requiere Python 3.11+ y [uv](https://docs.astral.sh/uv/). Las dependencias se instalan solas (el script las declara en su cabecera).

```bash
./md2pdf.py documento.md                # crea documento.pdf junto al .md
./md2pdf.py a.md b.md -o salida/        # varios archivos, carpeta de salida
./md2pdf.py carpeta/                    # todos los .md de la carpeta
```

Para usarlo desde cualquier lugar, enlázalo en tu `PATH`:

```bash
ln -s "$PWD/md2pdf.py" ~/.local/bin/md2pdf
md2pdf notas.md
```

## Navegador necesario

Pensado para **Linux y WSL**. Usa el primer navegador que encuentre, en este orden: Edge o Chrome de Windows (rutas `/mnt/c/Program Files...`, útil en WSL) y, después, `chromium`, `chromium-browser`, `google-chrome` o `microsoft-edge` del `PATH`. No hay soporte para macOS ni para Windows nativo por ahora. No necesita LaTeX ni `wkhtmltopdf`.

## Licencia

MIT. Ver [LICENSE](LICENSE).
