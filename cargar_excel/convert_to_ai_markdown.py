# #!/usr/bin/env python3
# """
# convert_to_ai_markdown.py

# Convierte PDF, PPT/PPTX, DOC/DOCX, XLS/XLSX y archivos de imagen a un paquete
# Markdown preparado para LLMs (Claude, ChatGPT, Gemini, etc.).

# Principio importante:
# - Markdown no puede representar fielmente todos los elementos visuales de Office/PDF
#   (colores, posiciones, SmartArt, gráficos, fuentes, animaciones, etc.).
# - Por eso el script conserva DOS capas:
#   1) contenido estructurado extraído (texto, tablas, metadatos);
#   2) una representación visual completa de cada página/diapositiva como PNG.
# - El .md referencia las imágenes. Así una IA puede leer el texto y, cuando sea
#   necesario, "ver" la diapositiva/página completa.

# Dependencias Python:
#     pip install pymupdf python-pptx python-docx openpyxl pillow pytesseract

# Dependencias externas recomendadas:
#     LibreOffice (para PPT/PPTX/DOC/DOCX/XLS/XLSX -> PDF)
#     Poppler (pdftoppm) opcional
#     Tesseract OCR opcional

# Ejemplos:
#     python convert_to_ai_markdown.py archivo.pptx
#     python convert_to_ai_markdown.py archivo.pdf
#     python convert_to_ai_markdown.py carpeta/ --recursive
#     python convert_to_ai_markdown.py archivo.pptx --ocr
#     python convert_to_ai_markdown.py archivo.pdf --dpi 180
# """

# from __future__ import annotations

# import argparse
# import hashlib
# import json
# import os
# import re
# import shutil
# import subprocess
# import sys
# import tempfile
# from pathlib import Path
# from typing import Iterable

# try:
#     import fitz  # PyMuPDF
# except ImportError:
#     print("Falta PyMuPDF. Instala: pip install pymupdf")
#     sys.exit(1)

# SUPPORTED = {
#     ".pdf", ".ppt", ".pptx", ".doc", ".docx",
#     ".xls", ".xlsx", ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"
# }


# def run(cmd: list[str], check=True) -> subprocess.CompletedProcess:
#     return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
#                           text=True, check=check)


# def which(name: str) -> str | None:
#     return shutil.which(name)


# def sha256_file(path: Path) -> str:
#     h = hashlib.sha256()
#     with path.open("rb") as f:
#         for chunk in iter(lambda: f.read(1024 * 1024), b""):
#             h.update(chunk)
#     return h.hexdigest()


# def find_libreoffice() -> str | None:
#     for name in ("libreoffice", "soffice"):
#         p = which(name)
#         if p:
#             return p
#     return None


# def convert_office_to_pdf(src: Path, workdir: Path) -> Path:
#     """
#     Usa LibreOffice en modo headless para convertir Office a PDF.
#     """
#     soffice = find_libreoffice()
#     if not soffice:
#         raise RuntimeError(
#             "No se encontró LibreOffice/soffice. "
#             "Instálalo para convertir archivos Office a PDF."
#         )

#     outdir = workdir / "office_pdf"
#     outdir.mkdir(parents=True, exist_ok=True)

#     result = run([
#         soffice, "--headless", "--convert-to", "pdf",
#         "--outdir", str(outdir), str(src)
#     ])

#     pdf = outdir / (src.stem + ".pdf")
#     if not pdf.exists():
#         raise RuntimeError(
#             f"LibreOffice no generó el PDF para {src.name}.\n"
#             f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
#         )
#     return pdf


# def extract_pdf_page_text(page: fitz.Page) -> str:
#     # "blocks" mantiene mejor el orden espacial que get_text("text")
#     blocks = page.get_text("blocks")
#     blocks = sorted(blocks, key=lambda b: (round(b[1], 1), round(b[0], 1)))

#     parts = []
#     for b in blocks:
#         text = b[4].strip()
#         if text:
#             parts.append(text)
#     return "\n\n".join(parts)


# def extract_links(page: fitz.Page) -> list[dict]:
#     links = []
#     for link in page.get_links():
#         uri = link.get("uri")
#         if uri:
#             links.append({
#                 "uri": uri,
#                 "rect": list(link.get("from", ()))
#             })
#     return links


# def extract_pdf_images(doc: fitz.Document, page: fitz.Page, asset_dir: Path,
#                        page_no: int) -> list[Path]:
#     """
#     Extrae imágenes embebidas cuando PyMuPDF puede recuperarlas.
#     La imagen de página completa se genera aparte y es la copia visual de respaldo.
#     """
#     paths = []
#     seen = set()

#     for idx, img in enumerate(page.get_images(full=True), start=1):
#         xref = img[0]
#         try:
#             base = doc.extract_image(xref)
#             data = base["image"]
#             ext = base.get("ext", "png")
#             digest = hashlib.sha1(data).hexdigest()[:12]
#             if digest in seen:
#                 continue
#             seen.add(digest)

#             p = asset_dir / f"page-{page_no:04d}-embedded-{idx:02d}-{digest}.{ext}"
#             p.write_bytes(data)
#             paths.append(p)
#         except Exception:
#             # No abortar: la página renderizada conserva la información visual.
#             pass

#     return paths


# def render_pdf_pages(pdf: Path, asset_dir: Path, dpi: int) -> list[Path]:
#     doc = fitz.open(pdf)
#     page_images = []

#     # Matriz de render. 150-220 DPI suele ser un buen equilibrio para LLMs.
#     scale = dpi / 72.0
#     matrix = fitz.Matrix(scale, scale)

#     for i, page in enumerate(doc, start=1):
#         pix = page.get_pixmap(matrix=matrix, alpha=False)
#         out = asset_dir / f"page-{i:04d}.png"
#         pix.save(out)
#         page_images.append(out)

#     doc.close()
#     return page_images


# def ocr_image(image_path: Path) -> str:
#     try:
#         import pytesseract
#         from PIL import Image
#     except ImportError:
#         return ""

#     try:
#         return pytesseract.image_to_string(Image.open(image_path)).strip()
#     except Exception:
#         return ""


# def markdown_escape(text: str) -> str:
#     text = text.replace("\x00", "")
#     return text


# def relative_link(path: Path, base: Path) -> str:
#     return path.relative_to(base).as_posix()


# def pdf_to_markdown(pdf: Path, output_dir: Path, source_name: str,
#                     dpi: int = 180, use_ocr: bool = False) -> Path:
#     output_dir.mkdir(parents=True, exist_ok=True)
#     assets = output_dir / "assets"
#     assets.mkdir(parents=True, exist_ok=True)

#     doc = fitz.open(pdf)
#     page_images = render_pdf_pages(pdf, assets, dpi)

#     md = []
#     md.append(f"# {source_name}\n")
#     md.append("> Documento convertido automáticamente para análisis por IA.\n")
#     md.append("> La imagen completa de cada página se conserva para evitar perder "
#               "colores, gráficos, diagramas, posiciones y elementos visuales.\n")
#     md.append(f"- Archivo original: `{source_name}`")
#     md.append(f"- Páginas: {len(doc)}")
#     md.append(f"- SHA-256: `{sha256_file(pdf)}`\n")
#     md.append("---\n")

#     manifest = {
#         "source": source_name,
#         "source_sha256": sha256_file(pdf),
#         "pages": []
#     }

#     for i, page in enumerate(doc, start=1):
#         text = extract_pdf_page_text(page)
#         links = extract_links(page)
#         embedded = extract_pdf_images(doc, page, assets, i)

#         if use_ocr and len(re.sub(r"\s+", "", text)) < 20:
#             ocr = ocr_image(page_images[i - 1])
#             if ocr:
#                 text = (text + "\n\n" + ocr).strip()

#         img_rel = relative_link(page_images[i - 1], output_dir)

#         md.append(f"## Página {i}\n")
#         md.append(f"![Representación visual completa — página {i}]({img_rel})\n")

#         if text:
#             md.append("### Texto extraído\n")
#             md.append("```text")
#             md.append(markdown_escape(text))
#             md.append("```\n")
#         else:
#             md.append("> No se detectó texto digital en esta página. "
#                       "La imagen completa se conserva para inspección visual.\n")

#         if links:
#             md.append("### Enlaces detectados\n")
#             for link in links:
#                 md.append(f"- {link['uri']}")
#             md.append("")

#         if embedded:
#             md.append("### Imágenes/recursos embebidos detectados\n")
#             for p in embedded:
#                 rel = relative_link(p, output_dir)
#                 md.append(f"- [{p.name}]({rel})")
#             md.append("")

#         manifest["pages"].append({
#             "page": i,
#             "visual_image": img_rel,
#             "text_characters": len(text),
#             "links": links,
#             "embedded_images": [relative_link(p, output_dir) for p in embedded]
#         })

#         md.append("---\n")

#     doc.close()

#     manifest_path = output_dir / "manifest.json"
#     manifest_path.write_text(
#         json.dumps(manifest, ensure_ascii=False, indent=2),
#         encoding="utf-8"
#     )

#     md_path = output_dir / f"{Path(source_name).stem}.md"
#     md_path.write_text("\n".join(md), encoding="utf-8")
#     return md_path


# def convert_single(src: Path, out_root: Path, dpi: int, use_ocr: bool) -> Path:
#     src = src.resolve()
#     digest = sha256_file(src)[:12]
#     target = out_root / f"{src.stem}_{digest}"
#     target.mkdir(parents=True, exist_ok=True)

#     ext = src.suffix.lower()

#     if ext == ".pdf":
#         return pdf_to_markdown(src, target, src.name, dpi, use_ocr)

#     if ext in {".ppt", ".pptx", ".doc", ".docx", ".xls", ".xlsx"}:
#         with tempfile.TemporaryDirectory(prefix="ai_md_") as tmp:
#             pdf = convert_office_to_pdf(src, Path(tmp))
#             # Copiar el PDF intermedio: sirve para auditoría/reproducibilidad.
#             copied_pdf = target / f"{src.stem}.pdf"
#             shutil.copy2(pdf, copied_pdf)
#             return pdf_to_markdown(
#                 copied_pdf, target, src.name, dpi, use_ocr
#             )

#     if ext in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}:
#         assets = target / "assets"
#         assets.mkdir(parents=True, exist_ok=True)
#         copied = assets / src.name
#         shutil.copy2(src, copied)

#         text = ocr_image(src) if use_ocr else ""
#         md = [
#             f"# {src.name}\n",
#             "![Imagen completa](assets/" + src.name + ")\n"
#         ]
#         if text:
#             md += ["## Texto OCR detectado\n", "```text", text, "```\n"]

#         md_path = target / f"{src.stem}.md"
#         md_path.write_text("\n".join(md), encoding="utf-8")
#         return md_path

#     raise ValueError(f"Formato no soportado: {src}")


# def discover_inputs(path: Path, recursive: bool) -> Iterable[Path]:
#     if path.is_file():
#         yield path
#         return

#     iterator = path.rglob("*") if recursive else path.glob("*")
#     for p in iterator:
#         if p.is_file() and p.suffix.lower() in SUPPORTED:
#             yield p


# def main():
#     parser = argparse.ArgumentParser(
#         description="Convierte documentos a Markdown enriquecido para IA."
#     )
#     parser.add_argument("input", type=Path,
#                         help="Archivo o carpeta de entrada.")
#     parser.add_argument("-o", "--output", type=Path, default=Path("ai_markdown"),
#                         help="Directorio de salida.")
#     parser.add_argument("--recursive", action="store_true",
#                         help="Procesar subcarpetas.")
#     parser.add_argument("--dpi", type=int, default=180,
#                         help="Resolución de imágenes de página (150-220 recomendado).")
#     parser.add_argument("--ocr", action="store_true",
#                         help="Ejecutar OCR en páginas con poco/no texto extraíble.")
#     args = parser.parse_args()

#     if not args.input.exists():
#         print(f"No existe: {args.input}")
#         sys.exit(2)

#     args.output.mkdir(parents=True, exist_ok=True)

#     files = list(discover_inputs(args.input, args.recursive))
#     if not files:
#         print("No se encontraron archivos compatibles.")
#         sys.exit(0)

#     print(f"Archivos encontrados: {len(files)}")

#     for src in files:
#         print(f"\nProcesando: {src}")
#         try:
#             md = convert_single(src, args.output, args.dpi, args.ocr)
#             print(f"OK -> {md}")
#         except Exception as exc:
#             print(f"ERROR -> {src}: {exc}")

#     print("\nProceso terminado.")


# if __name__ == "__main__":
#     main()
