"""批量将 assets/pages 下的 JPG/PNG 转为 WebP 并控制在 300KB 以下。"""
from pathlib import Path
from typing import Iterable, Tuple

from PIL import Image


PAGE_DIR = Path("number-sea-explorer/assets/pages")
MAX_DIM = 1400
SIZE_LIMIT = 300 * 1024
QUALITY_STEPS = (90, 80, 70, 60, 50, 40)
SCALE_STEPS = (1.0, 0.85, 0.75, 0.65, 0.55)


def iter_image_paths(directory: Path) -> Iterable[Path]:
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            yield path


def resize_image(im: Image.Image, scale: float) -> Image.Image:
    if scale == 1.0:
        return im
    new_size = (max(1, int(im.width * scale)), max(1, int(im.height * scale)))
    return im.resize(new_size, resample=Image.Resampling.LANCZOS)


def encode_webp(im: Image.Image, output: Path) -> int:
    for scale in SCALE_STEPS:
        resized = resize_image(im, scale)
        for quality in QUALITY_STEPS:
            resized.save(output, format="WEBP", quality=quality, method=6)
            if output.stat().st_size <= SIZE_LIMIT:
                return output.stat().st_size
    return output.stat().st_size


def convert(path: Path) -> Tuple[Path, int]:
    output = path.with_suffix(".webp")
    with Image.open(path) as im:
        im = im.convert("RGBA") if path.suffix.lower() == ".png" else im.convert("RGB")
        if max(im.width, im.height) > MAX_DIM:
            ratio = MAX_DIM / max(im.width, im.height)
            im = im.resize((int(im.width * ratio), int(im.height * ratio)), Image.Resampling.LANCZOS)
        final_size = encode_webp(im, output)
    return path, final_size


def main() -> None:
    if not PAGE_DIR.exists():
        raise SystemExit(f"{PAGE_DIR} 不存在")
    for img_path in iter_image_paths(PAGE_DIR):
        legacy_size = img_path.stat().st_size
        _, final_size = convert(img_path)
        print(f"{img_path.name}: {legacy_size//1024}KB -> {final_size//1024}KB")
        img_path.unlink()


if __name__ == "__main__":
    main()
