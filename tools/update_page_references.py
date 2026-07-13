"""将所有页面资源引用统一指向 WebP 格式。"""
from pathlib import Path


PAGE_DIR = Path("number-sea-explorer/assets/pages")
TARGET_FILES = [
    Path("number-sea-explorer/data/questions.json"),
    Path("数海漫游-单文件静态版.html"),
    Path("number-sea-explorer/imsmanifest.xml"),
]


def main() -> None:
    if not PAGE_DIR.exists():
        raise SystemExit(f"{PAGE_DIR} 不存在")
    bases = sorted(path.stem for path in PAGE_DIR.glob("*.webp"))
    for target in TARGET_FILES:
        if not target.exists():
            print(f"跳过不存在的文件：{target}")
            continue
        content = target.read_text(encoding="utf-8")
        updated = content
        for base in bases:
            for prefix in ("assets/pages/", "number-sea-explorer/assets/pages/"):
                for old_ext in (".png", ".jpg"):
                    old = f"{prefix}{base}{old_ext}"
                    new = f"{prefix}{base}.webp"
                    updated = updated.replace(old, new)
        if updated != content:
            target.write_text(updated, encoding="utf-8")
            print(f"{target} 已切换为 WebP")


if __name__ == "__main__":
    main()
