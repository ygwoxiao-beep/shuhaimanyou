#!/usr/bin/env python3
from PIL import Image, ImageFilter
import numpy as np
import os

ASSETS_DIR = "assets/pages"
LOGO_PATH = "/Users/eeo/.cursor/projects/Users-eeo-xiao-cursor-number-sea-explorer/assets/image-99fbb279-763f-47ff-a3ee-5254b04b21ad.png"

def detect_logo_bbox(img):
    """Detect a candidate logo bbox in the bottom area using color heuristics.
    Returns (x, y, w, h) or None if not found."""
    rgb = img.convert("RGB")
    arr = np.array(rgb)
    h, w, _ = arr.shape

    y_start = int(h * 0.6)
    mask = np.zeros((h, w), dtype=bool)

    # Heuristic thresholds
    for yy in range(y_start, h):
        row = arr[yy]
        # vectorized test for green-ish or very light (white) pixels
        r = row[:, 0].astype(int)
        g = row[:, 1].astype(int)
        b = row[:, 2].astype(int)
        green_cond = (g > 140) & (g - r > 20) & (g - b > 10)
        white_cond = (r + g + b) > 700  # nearly white
        mask[yy] = green_cond | white_cond

    # If no candidate pixels, return None
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None

    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())

    # Expand bbox slightly
    pad_x = max(8, int((x1 - x0) * 0.05))
    pad_y = max(6, int((y1 - y0) * 0.05))
    x0 = max(0, x0 - pad_x)
    y0 = max(0, y0 - pad_y)
    x1 = min(w - 1, x1 + pad_x)
    y1 = min(h - 1, y1 + pad_y)

    bw = x1 - x0 + 1
    bh = y1 - y0 + 1

    # sanity checks: bounding box should be within reasonable size (not whole image)
    if bw < 30 or bh < 15 or bw > w * 0.6 or bh > h * 0.6:
        return None

    return (x0, y0, bw, bh)

def fill_bbox_with_neighbor(img, bbox):
    """Fill bbox by copying pixels from above (preferred) or left, then blur seams."""
    x, y, bw, bh = bbox
    w, h = img.size

    # prefer region directly above
    src_y = max(0, y - bh - 8)
    src_x = x
    if src_y + bh > h:
        src_y = max(0, y - bh)

    # if above region is too small or overlaps, try left
    if src_y < 0 or src_y + bh > h:
        src_y = max(0, y - bh - 8)

    if src_y >= 0:
        src_box = (src_x, src_y, src_x + bw, src_y + bh)
        # if src_box exceeds bounds, adjust
        if src_box[2] > w:
            src_box = (w - bw, src_box[1], w, src_box[3])
        if src_box[1] < 0:
            src_box = (src_box[0], 0, src_box[2], bh)
    else:
        # fallback to left area
        src_x = max(0, x - bw - 8)
        src_y = y
        src_box = (src_x, src_y, src_x + bw, src_y + bh)
        if src_box[2] > w:
            src_box = (w - bw, src_box[1], w, src_box[3])

    # If source box still out of bounds, clamp
    sx0 = max(0, src_box[0])
    sy0 = max(0, src_box[1])
    sx1 = min(w, src_box[2])
    sy1 = min(h, src_box[3])

    if sx1 - sx0 != bw or sy1 - sy0 != bh:
        # If source region not full size, try taking a nearby tile or replicate edge
        src = img.crop((max(0, x), max(0, y - bh - 8), min(w, x + bw), max(0, y - 8)))
        # If src smaller, resize to fit
        if src.size[0] == 0 or src.size[1] == 0:
            return img
        src = src.resize((bw, bh), Image.LANCZOS)
    else:
        src = img.crop((sx0, sy0, sx1, sy1))

    # Paste source over bbox
    out = img.copy()
    out.paste(src, (x, y))

    # Soften seam by blurring a slightly larger region and pasting blended
    blur_radius = max(2, int(min(bw, bh) * 0.03))
    # create blurred version of full image and paste only bbox area blurred
    blurred = out.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    # Create simple rectangular mask with soft edges
    edge = Image.new("L", (bw, bh), 0)
    edge_draw = edge.load()
    # create a distance-based alpha fade
    for yy in range(bh):
        for xx in range(bw):
            dx = min(xx, bw - 1 - xx)
            dy = min(yy, bh - 1 - yy)
            d = min(dx, dy)
            edge_threshold = int(min(10, max(3, min(bw, bh) * 0.08)))
            if d < edge_threshold:
                fade = int(255 * (d / edge_threshold))
            else:
                fade = 255
            edge_draw[xx, yy] = fade
    out.paste(blurred.crop((x, y, x + bw, y + bh)), (x, y), edge)
    return out

def template_match_logo(img, logo_path):
    """Try to locate logo by scaled template matching in bottom area. Returns bbox or None."""
    try:
        logo = Image.open(logo_path).convert("RGB")
    except Exception:
        return None
    main = img.convert("RGB")
    main_arr = np.array(main, dtype=np.int16)
    mh, mw, _ = main_arr.shape

    # search region: bottom 50%
    y0 = int(mh * 0.5)
    best = (None, float('inf'), 1.0)
    for scale in [1.0, 0.8, 0.6, 0.5, 0.45, 0.42, 0.4, 0.35, 0.3]:
        lw = max(10, int(logo.width * scale))
        lh = max(6, int(logo.height * scale))
        logo_resized = logo.resize((lw, lh), Image.LANCZOS)
        logo_arr = np.array(logo_resized, dtype=np.int16)

        # step to speed up
        step = max(4, int(min(lw, lh) / 6))
        for yy in range(y0, mh - lh + 1, step):
            for xx in range(0, mw - lw + 1, step):
                patch = main_arr[yy:yy+lh, xx:xx+lw]
                if patch.shape[:2] != logo_arr.shape[:2]:
                    continue
                diff = np.mean(np.abs(patch - logo_arr))
                if diff < best[1]:
                    best = ((xx, yy, lw, lh), float(diff), scale)
        # early stop if very good match
        if best[1] < 25:
            break

    if best[0] is not None and best[1] < 60:
        return best[0]
    return None

def process_all(dry_run=False):
    files = sorted([f for f in os.listdir(ASSETS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    processed = 0
    for fn in files:
        path = os.path.join(ASSETS_DIR, fn)
        try:
            img = Image.open(path).convert("RGB")
        except Exception as e:
            print(f"Skipping {fn}: cannot open ({e})")
            continue
        # First try heuristic color detection
        bbox = detect_logo_bbox(img)
        # If heuristic failed, try template matching against reference logo
        if not bbox:
            tpl = template_match_logo(img, LOGO_PATH)
            if tpl:
                bbox = tpl
            else:
                print(f"{fn}: logo not detected, skipping")
                continue

        x, y, bw, bh = bbox
        print(f"{fn}: detected logo bbox at ({x},{y}) size {bw}x{bh}")

        out = fill_bbox_with_neighbor(img, bbox)

        if not dry_run:
            # Preserve format: JPEG/PNG
            if fn.lower().endswith(('.jpg', '.jpeg')):
                out.save(path, "JPEG", quality=95)
            else:
                out.save(path, "PNG")
        processed += 1

    print(f"Processed {processed}/{len(files)} files")

if __name__ == '__main__':
    process_all(dry_run=False)
