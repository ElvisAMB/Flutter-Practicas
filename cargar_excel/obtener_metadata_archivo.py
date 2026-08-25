#!/usr/bin/env python3
"""
file_metadata.py — Extrae metadatos de un archivo.

Tres capas de información:
  1. Sistema de archivos (siempre): tamaño, tiempos, permisos, propietario, inodo.
  2. Identificación de tipo: extensión, MIME por extensión y firma de bytes (magic number).
  3. Metadatos embebidos (según formato y librerías disponibles):
       - Imágenes  -> Pillow (EXIF, GPS)
       - PDF       -> pypdf
       - OOXML     -> zipfile + xml (docx/xlsx/pptx, sin dependencias)
       - Audio     -> mutagen (opcional)

Uso:
    python3 file_metadata.py archivo.pdf
    python3 file_metadata.py imagen.jpg --json
    python3 file_metadata.py video.mp4 --hash sha256 md5
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import stat
import sys
import zipfile
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Metadatos del sistema de archivos
# ---------------------------------------------------------------------------

def _ts(epoch: float) -> str:
    """Epoch -> ISO-8601 en hora local con offset explícito."""
    return datetime.fromtimestamp(epoch).astimezone().isoformat()


def human_size(n: int) -> str:
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(n) < 1024 or unit == "TiB":
            return f"{n:.2f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n} B"


def filesystem_metadata(path: Path) -> dict:
    st = path.lstat()  # lstat: no sigue enlaces simbólicos
    info = {
        "nombre": path.name,
        "ruta_absoluta": str(path.resolve()),
        "extension": path.suffix.lower() or None,
        "tamano_bytes": st.st_size,
        "tamano_legible": human_size(st.st_size),
        "es_enlace_simbolico": path.is_symlink(),
        "modificado": _ts(st.st_mtime),
        "accedido": _ts(st.st_atime),
        "metadatos_cambiados_ctime": _ts(st.st_ctime),
        "permisos_octal": oct(st.st_mode & 0o777),
        "permisos_simbolicos": stat.filemode(st.st_mode),
        "inodo": st.st_ino,
        "enlaces_duros": st.st_nlink,
        "uid": st.st_uid,
        "gid": st.st_gid,
    }

    # st_birthtime solo existe en macOS/BSD y en Linux >= 3.12 con statx.
    birth = getattr(st, "st_birthtime", None)
    info["creado"] = _ts(birth) if birth else None

    if path.is_symlink():
        info["apunta_a"] = os.readlink(path)

    try:  # nombres de usuario/grupo: solo POSIX
        import grp
        import pwd
        info["propietario"] = pwd.getpwuid(st.st_uid).pw_name
        info["grupo"] = grp.getgrgid(st.st_gid).gr_name
    except (ImportError, KeyError):
        pass

    return info


# ---------------------------------------------------------------------------
# 2. Identificación de tipo por firma de bytes
# ---------------------------------------------------------------------------

SIGNATURES = [
    (b"\x89PNG\r\n\x1a\n", 0, "image/png"),
    (b"\xff\xd8\xff", 0, "image/jpeg"),
    (b"GIF87a", 0, "image/gif"),
    (b"GIF89a", 0, "image/gif"),
    (b"BM", 0, "image/bmp"),
    (b"%PDF-", 0, "application/pdf"),
    (b"PK\x03\x04", 0, "zip u OOXML (docx/xlsx/pptx/odf/jar)"),
    (b"\x1f\x8b", 0, "application/gzip"),
    (b"7z\xbc\xaf\x27\x1c", 0, "application/x-7z-compressed"),
    (b"Rar!\x1a\x07", 0, "application/vnd.rar"),
    (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", 0, "MS Office legado (doc/xls/ppt)"),
    (b"\x7fELF", 0, "application/x-executable (ELF)"),
    (b"ID3", 0, "audio/mpeg"),
    (b"OggS", 0, "audio/ogg"),
    (b"fLaC", 0, "audio/flac"),
    (b"RIFF", 0, "RIFF (wav/avi/webp)"),
    (b"ftyp", 4, "MP4/MOV/HEIF"),
    (b"\x00\x00\x01\xba", 0, "video/mpeg"),
]


def sniff_type(path: Path) -> dict:
    with path.open("rb") as f:
        head = f.read(32)

    detectado = next(
        (t for sig, off, t in SIGNATURES if head[off:off + len(sig)] == sig),
        None,
    )
    if detectado is None and head and all(c == 0 or 32 <= c < 127 or c in (9, 10, 13) for c in head):
        detectado = "text/plain (probable)"

    mime_ext, _ = mimetypes.guess_type(path.name)
    return {
        "mime_por_extension": mime_ext,
        "mime_por_firma": detectado,
        "cabecera_hex": head[:16].hex(" "),
        "extension_coherente": _coherente(mime_ext, detectado, path.suffix.lower()),
    }


ZIP_BASADOS = {
    ".zip", ".docx", ".xlsx", ".pptx", ".docm", ".xlsm", ".pptm",
    ".odt", ".ods", ".odp", ".jar", ".epub", ".apk", ".whl",
}


def _coherente(mime_ext: str | None, firma: str | None, ext: str) -> bool | None:
    """True/False si se puede comparar; None si no hay datos suficientes.

    Un False no prueba manipulación maliciosa: lo más común es una extensión
    equivocada o un formato que este script no reconoce.
    """
    if not firma:
        return None
    if firma.startswith("zip"):
        return ext in ZIP_BASADOS
    if not mime_ext or "/" not in firma:
        return None
    return firma.split(" ")[0].split("/")[0] == mime_ext.split("/")[0]


# ---------------------------------------------------------------------------
# 3. Hashes (lectura por bloques: no carga el archivo en memoria)
# ---------------------------------------------------------------------------

def compute_hashes(path: Path, algos: list[str], chunk: int = 1 << 20) -> dict:
    hs = {a: hashlib.new(a) for a in algos}
    with path.open("rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            for h in hs.values():
                h.update(block)
    return {a: h.hexdigest() for a, h in hs.items()}


# ---------------------------------------------------------------------------
# 4. Metadatos embebidos por formato
# ---------------------------------------------------------------------------

def _exif_gps(gps: dict) -> dict | None:
    """Convierte GPSInfo (grados/minutos/segundos) a decimal."""
    def to_deg(vals):
        d, m, s = (float(v) for v in vals)
        return d + m / 60 + s / 3600
    try:
        lat = to_deg(gps[2]) * (-1 if gps[1] == "S" else 1)
        lon = to_deg(gps[4]) * (-1 if gps[3] == "W" else 1)
        return {"latitud": round(lat, 6), "longitud": round(lon, 6)}
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return None


def image_metadata(path: Path) -> dict | None:
    try:
        from PIL import Image
        from PIL.ExifTags import GPSTAGS, TAGS
    except ImportError:
        return {"_aviso": "instala Pillow para metadatos de imagen (pip install Pillow)"}

    try:
        with Image.open(path) as img:
            data = {
                "formato": img.format,
                "modo_color": img.mode,
                "dimensiones": f"{img.width}x{img.height}",
                "animada": getattr(img, "n_frames", 1) > 1,
            }
            exif = img.getexif()
            if exif:
                tags = {TAGS.get(k, k): v for k, v in exif.items()}
                gps_raw = exif.get_ifd(0x8825)
                if gps_raw:
                    gps = {GPSTAGS.get(k, k): v for k, v in gps_raw.items()}
                    tags["GPS"] = _exif_gps(gps_raw) or gps
                data["exif"] = {
                    k: (str(v)[:200] if not isinstance(v, (int, float, dict)) else v)
                    for k, v in tags.items()
                }
            return data
    except Exception as e:  # archivo corrupto, formato no soportado, etc.
        return {"_error": f"{type(e).__name__}: {e}"}


def pdf_metadata(path: Path) -> dict | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        return {"_aviso": "instala pypdf para metadatos de PDF (pip install pypdf)"}

    try:
        reader = PdfReader(path)
        data = {"paginas": len(reader.pages), "cifrado": reader.is_encrypted}
        if reader.metadata:
            data["info"] = {
                k.lstrip("/"): str(v) for k, v in reader.metadata.items()
            }
        return data
    except Exception as e:
        return {"_error": f"{type(e).__name__}: {e}"}


OOXML_CORE = "docProps/core.xml"
OOXML_APP = "docProps/app.xml"


def ooxml_metadata(path: Path) -> dict | None:
    """docx/xlsx/pptx: los metadatos son XML dentro del ZIP. Sin dependencias."""
    import xml.etree.ElementTree as ET

    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            if OOXML_CORE not in names:
                return None
            data = {}
            for part in (OOXML_CORE, OOXML_APP):
                if part not in names:
                    continue
                root = ET.fromstring(z.read(part))
                for el in root:
                    tag = el.tag.split("}")[-1]
                    if el.text and el.text.strip():
                        data[tag] = el.text.strip()
            return data or None
    except (zipfile.BadZipFile, ET.ParseError) as e:
        return {"_error": f"{type(e).__name__}: {e}"}


def audio_metadata(path: Path) -> dict | None:
    try:
        import mutagen
    except ImportError:
        return {"_aviso": "instala mutagen para metadatos de audio/video (pip install mutagen)"}

    try:
        f = mutagen.File(path, easy=True)
        if f is None:
            return None
        data = {k: v for k, v in (f.tags or {}).items()}
        if f.info:
            data["_duracion_seg"] = round(getattr(f.info, "length", 0), 2)
            data["_bitrate"] = getattr(f.info, "bitrate", None)
        return data
    except Exception as e:
        return {"_error": f"{type(e).__name__}: {e}"}


EXTRACTORES = {
    ".jpg": image_metadata, ".jpeg": image_metadata, ".png": image_metadata,
    ".gif": image_metadata, ".bmp": image_metadata, ".tiff": image_metadata,
    ".tif": image_metadata, ".webp": image_metadata, ".heic": image_metadata,
    ".pdf": pdf_metadata,
    ".docx": ooxml_metadata, ".xlsx": ooxml_metadata, ".pptx": ooxml_metadata,
    ".docm": ooxml_metadata, ".xlsm": ooxml_metadata,
    ".mp3": audio_metadata, ".flac": audio_metadata, ".ogg": audio_metadata,
    ".m4a": audio_metadata, ".wav": audio_metadata, ".mp4": audio_metadata,
}


# ---------------------------------------------------------------------------
# Orquestación y salida
# ---------------------------------------------------------------------------

def extract(path: Path, algos: list[str] | None = None) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"No existe: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"Es un directorio, no un archivo: {path}")

    result = {
        "sistema_de_archivos": filesystem_metadata(path),
        "tipo": sniff_type(path),
    }
    if algos:
        result["hashes"] = compute_hashes(path, algos)

    extractor = EXTRACTORES.get(path.suffix.lower())
    if extractor:
        embebidos = extractor(path)
        if embebidos:
            result["metadatos_embebidos"] = embebidos
    else:
        result["metadatos_embebidos"] = None

    return result


def print_human(data: dict) -> None:
    for seccion, contenido in data.items():
        print(f"\n=== {seccion.replace('_', ' ').upper()} ===")
        if contenido is None:
            print("  (sin extractor específico para esta extensión)")
            continue
        for k, v in contenido.items():
            if isinstance(v, dict):
                print(f"  {k}:")
                for sk, sv in v.items():
                    print(f"      {sk}: {sv}")
            else:
                print(f"  {k}: {v}")


def main() -> int:
    p = argparse.ArgumentParser(description="Extrae metadatos de un archivo.")
    p.add_argument("archivo", type=Path)
    p.add_argument("--json", action="store_true", help="salida JSON")
    p.add_argument(
        "--hash", nargs="*", default=None, metavar="ALGO",
        help="calcula hashes (por defecto sha256 si se usa sin valores)",
    )
    args = p.parse_args()

    algos = None
    if args.hash is not None:
        algos = args.hash or ["sha256"]
        desconocidos = [a for a in algos if a not in hashlib.algorithms_available]
        if desconocidos:
            p.error(f"algoritmo(s) no disponible(s): {', '.join(desconocidos)}")

    try:
        data = extract(args.archivo, algos)
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    else:
        print_human(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())