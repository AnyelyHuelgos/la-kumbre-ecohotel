"""Reduce the size of static images without renaming them, and disable old MP4 assets.

Run at the repository root. Original media remains recoverable from the
respaldo-antes-de-optimizar-20261013 branch.
"""
from __future__ import annotations

from pathlib import Path
import os
import tempfile

from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "kumbre" / "static" / "img"
VIDEO_DIR = ROOT / "kumbre" / "static" / "videos"
MAX_DIMENSION = 2560
JPEG_QUALITY = 82
WEBP_QUALITY = 82
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def mb(size: int) -> float:
    return round(size / 1024 / 1024, 2)


def optimize_one(path: Path) -> tuple[int, int, bool]:
    original_bytes = path.stat().st_size
    temporary_path = None
    try:
        with Image.open(path) as source:
            icc_profile = source.info.get("icc_profile")
            image = ImageOps.exif_transpose(source)
            image.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
            suffix = path.suffix.lower()
            if suffix in (".jpg", ".jpeg"):
                if image.mode not in ("L", "RGB"):
                    image = image.convert("RGB")
                format_name = "JPEG"
                parameters = {"quality": JPEG_QUALITY, "optimize": True, "progressive": True}
            elif suffix == ".webp":
                format_name = "WEBP"
                parameters = {"quality": WEBP_QUALITY, "method": 6}
            else:
                format_name = "PNG"
                parameters = {"optimize": True, "compress_level": 9}
            if icc_profile:
                parameters["icc_profile"] = icc_profile
            fd, tmp_name = tempfile.mkstemp(prefix="kumbre-media-", suffix=suffix, dir=path.parent)
            os.close(fd)
            temporary_path = Path(tmp_name)
            image.save(temporary_path, format=format_name, **parameters)
        optimized_bytes = temporary_path.stat().st_size
        if optimized_bytes < original_bytes * 0.95:
            os.replace(temporary_path, path)
            temporary_path = None
            return original_bytes, optimized_bytes, True
        return original_bytes, original_bytes, False
    except (OSError, ValueError, UnidentifiedImageError) as exc:
        print(f"SKIP {path.name}: {exc}")
        return original_bytes, original_bytes, False
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def hide_temporarily_unavailable_video() -> None:
    template = ROOT / "kumbre" / "templates" / "nosotros.html"
    text = template.read_text(encoding="utf-8")
    before = """                        <div class="video-thumbnail" id="videoThumbnail">
                            <img src="{% static 'img/entrada.jpg' %}" alt="Video de La Kumbre">
                            <div class="play-button">
                                <i class="fas fa-play"></i>
                            </div>
                        </div>
                        <!-- Hidden video that will be shown on click -->
                        <video id="experienceVideo" preload="metadata">
                            <source src="{% static 'videos/Como-llegar.mp4' %}" type="video/mp4">
                            Tu navegador no soporta el elemento de video.
                        </video>"""
    after = """                        <div class="video-thumbnail" style="cursor: default;">
                            <img src="{% static 'img/entrada.jpg' %}" alt="Fotografia de La Kumbre">
                        </div>"""
    if before not in text:
        raise RuntimeError("No se encontro el bloque esperado de video en nosotros.html; no se modifico")
    text = text.replace(before, after, 1)
    text = text.replace('console.error("Could not find video elements!");', "// Video deshabilitado temporalmente: se muestra una fotografia.", 1)
    template.write_text(text, encoding="utf-8")


def main() -> None:
    paths = sorted(p for p in IMAGE_DIR.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS)
    original_total = 0
    compressed_total = 0
    count = 0
    for path in paths:
        old, new, changed = optimize_one(path)
        original_total += old
        compressed_total += new
        if changed:
            count += 1
            print(f"OPTIMIZED {path.relative_to(ROOT)}: {mb(old)} -> {mb(new)} MiB")

    # Keep the PDF documents stored beside the videos.
    removed_videos = []
    for path in sorted(VIDEO_DIR.glob("*.mp4")):
        removed_videos.append((path.name, mb(path.stat().st_size)))
        path.unlink()
    hide_temporarily_unavailable_video()
    print(f"IMAGES: {len(paths)} reviewed; {count} reduced")
    print(f"IMAGE TOTAL: {mb(original_total)} -> {mb(compressed_total)} MiB")
    print(f"VIDEOS REMOVED: {removed_videos}")
    print("PDF documents were preserved.")


if __name__ == "__main__":
    main()
