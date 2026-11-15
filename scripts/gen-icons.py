"""
WBit 图标生成器（纯 Python 标准库，无第三方依赖）
生成 PWA / 桌面端所需的全部图标：
  site/assets/icons/*.png|svg
  desktop/src-tauri/icons/*.png|ico|icns
用法：python scripts/gen-icons.py
"""
import math
import os
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PWA_DIR = ROOT / "site" / "assets" / "icons"
TAURI_DIR = ROOT / "desktop" / "src-tauri" / "icons"
PWA_DIR.mkdir(parents=True, exist_ok=True)
TAURI_DIR.mkdir(parents=True, exist_ok=True)

# WBit 品牌配色：深蓝 → 天青 → 薄荷绿
STOPS = [
    (0.00, (38, 96, 235)),    # #2660EB
    (0.55, (0, 190, 255)),    # #00BEFF
    (1.00, (35, 230, 160)),   # #23E6A0
]


def lerp(a, b, t):
    return a + (b - a) * t


def gradient(t):
    t = max(0.0, min(1.0, t))
    for i in range(len(STOPS) - 1):
        p0, c0 = STOPS[i]
        p1, c1 = STOPS[i + 1]
        if t <= p1:
            k = (t - p0) / (p1 - p0)
            return tuple(int(round(lerp(c0[j], c1[j], k))) for j in range(3))
    return STOPS[-1][1]


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def seg_dist(px_, py_, x0, y0, x1, y1):
    """点到线段的最短距离"""
    vx, vy = x1 - x0, y1 - y0
    wx, wy = px_ - x0, py_ - y0
    t = clamp((wx * vx + wy * vy) / (vx * vx + vy * vy))
    dx, dy = px_ - (x0 + t * vx), py_ - (y0 + t * vy)
    return math.sqrt(dx * dx + dy * dy)


# ── 品牌几何 ─────────────────────────────────────────────────
# W 字标：4 段笔画，落笔粗、收笔细（书写感）；坐标为 0~1 归一化
W_NODES = [
    ((0.2575, 0.2975), 0.052),
    ((0.3875, 0.7025), 0.075),
    ((0.5000, 0.4325), 0.052),
    ((0.6125, 0.7025), 0.075),
    ((0.7425, 0.2975), 0.052),
]

# 轨道环：倾斜椭圆。上弧压在 W 之上、下弧从 W 背后穿过 —— 形成「环套住字」的立体交叉
RING_RX, RING_RY = 0.395, 0.150
RING_TILT = -24.0
RING_HALF = 0.0156
RING_RGB = (11, 58, 110)
RING_FRONT, RING_BACK = 0.62, 0.34

# W 外描边：柔和的深蓝光晕，让白字与底色/环拉开层次
W_HALO = 0.026


def unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dy)
    return (dx / ln, dy / ln) if ln > 1e-9 else (0.0, 0.0)


def node_normal(pts, i):
    """折线在第 i 个顶点处的法向（角平分线方向）"""
    if i == 0:
        d = unit(pts[0], pts[1])
    elif i == len(pts) - 1:
        d = unit(pts[-2], pts[-1])
    else:
        d1, d2 = unit(pts[i - 1], pts[i]), unit(pts[i], pts[i + 1])
        d = (d1[0] + d2[0], d1[1] + d2[1])
        ln = math.hypot(*d)
        d = d1 if ln < 1e-9 else (d[0] / ln, d[1] / ln)
    return (-d[1], d[0])


def w_svg_path(scale=40.0):
    """把 W_NODES 转成 SVG 填充路径（与光栅化共用同一套几何）"""
    pts = [(p[0] * scale, p[1] * scale) for p, _ in W_NODES]
    ws = [w * scale for _, w in W_NODES]
    left, right = [], []
    for i, p in enumerate(pts):
        nx, ny = node_normal(pts, i)
        half = ws[i] / 2
        left.append((p[0] + nx * half, p[1] + ny * half))
        right.append((p[0] - nx * half, p[1] - ny * half))
    d = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in left)
    d += " L " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in reversed(right)) + " Z"
    return d


def w_ring_svg(scale=40.0, front=True):
    """轨道环的上下两段弧（front=True 为压在 W 上的那一半）"""
    rx, ry = RING_RX * scale, RING_RY * scale
    cx = cy = scale / 2
    a = math.radians(RING_TILT)
    dx, dy = rx * math.cos(a), rx * math.sin(a)
    x0, y0 = cx - dx, cy - dy
    x1, y1 = cx + dx, cy + dy
    sweep = 1 if front else 0
    return (f"M{x0:.2f} {y0:.2f}A{rx:.2f} {ry:.2f} {RING_TILT:.0f} 0 {sweep} {x1:.2f} {y1:.2f}")


def seg_cov(u, v, p0, p1, w0, w1, aa):
    """变宽度线段（圆头）的覆盖率，用于抗锯齿描边"""
    vx, vy = p1[0] - p0[0], p1[1] - p0[1]
    l2 = vx * vx + vy * vy
    wx, wy = u - p0[0], v - p0[1]
    t = (wx * vx + wy * vy) / l2
    tc = clamp(t)
    d = abs(wx * vy - wy * vx) / math.sqrt(l2) - lerp(w0, w1, tc) / 2
    if t < 0.0:
        d = max(d, math.hypot(wx, wy) - w0 / 2)
    elif t > 1.0:
        d = max(d, math.hypot(u - p1[0], v - p1[1]) - w1 / 2)
    return clamp(0.5 - d / aa)


def w_cov(u, v, aa=0.007):
    """W 字标的覆盖率（取各段最大值）"""
    best = 0.0
    for i in range(len(W_NODES) - 1):
        (x0, y0), w0 = W_NODES[i]
        (x1, y1), w1 = W_NODES[i + 1]
        c = seg_cov(u, v, (x0, y0), (x1, y1), w0, w1, aa)
        if c > best:
            best = c
    return best


def render(size, radius=0.22):
    """渐变底 + 交叉轨道环（环与 W 互相穿插）+ 变宽度 W 字标。
    radius=0 时输出满幅方块（用于圆形头像）。"""
    px = bytearray(size * size * 4)
    ang = math.radians(RING_TILT)
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    rc_r, rc_g, rc_b = RING_RGB
    for y in range(size):
        v = (y + 0.5) / size
        for x in range(size):
            u = (x + 0.5) / size

            # 外轮廓：圆角方块（radius>0）或满幅方块（radius=0）
            if radius > 0.0:
                dx = abs(u - 0.5) - (0.5 - radius)
                dy = abs(v - 0.5) - (0.5 - radius)
                d = math.sqrt(max(dx, 0) ** 2 + max(dy, 0) ** 2) + min(max(dx, dy), 0.0) - radius
            else:
                d = max(abs(u - 0.5), abs(v - 0.5)) - 0.5
            alpha = clamp(0.5 - d * size)
            if alpha <= 0:
                continue

            r, g, b = gradient((u + v) / 2)

            # 右上角柔光
            glow = clamp(1.0 - math.hypot((u - 0.76) * 1.1, (v - 0.20) * 1.1) / 0.66) ** 2 * 0.26
            if glow > 0.0:
                r, g, b = lerp(r, 255, glow), lerp(g, 255, glow), lerp(b, 255, glow)

            # 轨道环：用旋转坐标判断像素落在前半还是后半
            xr = (u - 0.5) * cos_a + (v - 0.5) * sin_a
            yr = -(u - 0.5) * sin_a + (v - 0.5) * cos_a
            q = math.sqrt((xr / RING_RX) ** 2 + (yr / RING_RY) ** 2)
            ring = clamp((RING_HALF - abs(q - 1.0) * RING_RX) / 0.007)
            back = ring * RING_BACK if yr >= 0.0 else 0.0
            front = ring * RING_FRONT if yr < 0.0 else 0.0

            # ① 下弧：W 之前（从字背后穿过）
            if back > 0.0:
                r, g, b = lerp(r, rc_r, back), lerp(g, rc_g, back), lerp(b, rc_b, back)

            # ② W 本体（白）+ 柔光描边
            if 0.18 < u < 0.82 and 0.24 < v < 0.78:
                cov = w_cov(u, v)
                if cov > 0.0:
                    r, g, b = lerp(r, 255, cov), lerp(g, 255, cov), lerp(b, 255, cov)
                else:
                    halo = w_cov(u, v, W_HALO) * 0.30
                    if halo > 0.0:
                        r, g, b = lerp(r, 6, halo), lerp(g, 38, halo), lerp(b, 86, halo)

            # ③ 上弧：压在 W 之上
            if front > 0.0:
                r, g, b = lerp(r, rc_r, front), lerp(g, rc_g, front), lerp(b, rc_b, front)

            i = (y * size + x) * 4
            px[i] = int(round(r))
            px[i + 1] = int(round(g))
            px[i + 2] = int(round(b))
            px[i + 3] = int(round(alpha * 255))
    return bytes(px)


def png_chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def make_png(size, radius=0.22):
    raw = bytearray()
    row = render(size, radius)
    stride = size * 4
    for y in range(size):
        raw.append(0)  # filter type 0
        raw.extend(row[y * stride:(y + 1) * stride])
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", ihdr)
            + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + png_chunk(b"IEND", b""))


def make_ico(sizes):
    images = [(s, make_png(s)) for s in sizes]
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries, body = b"", b""
    for s, data in images:
        w = 0 if s >= 256 else s
        entries += struct.pack("<BBBBHHII", w, w, 0, 0, 1, 32, len(data), offset)
        body += data
        offset += len(data)
    return header + entries + body


def make_icns(sizes):
    # PNG-based ICNS：ic07=128, ic08=256, ic09=512, ic10=1024
    types = {128: b"ic07", 256: b"ic08", 512: b"ic09", 1024: b"ic10"}
    chunks = b""
    for s in sizes:
        data = make_png(s)
        chunks += types[s] + struct.pack(">I", 8 + len(data)) + data
    return b"icns" + struct.pack(">I", 8 + len(chunks)) + chunks


SVG = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="40" height="40" role="img" aria-label="WBit">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#2660EB"/><stop offset="0.55" stop-color="#00BEFF"/><stop offset="1" stop-color="#23E6A0"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.74" cy="0.18" r="0.9">
      <stop offset="0" stop-color="#fff" stop-opacity=".30"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="clip"><rect width="40" height="40" rx="9"/></clipPath>
  </defs>
  <g clip-path="url(#clip)">
    <rect width="40" height="40" fill="url(#g)"/>
    <rect width="40" height="40" fill="url(#glow)"/>
    <path d="{w_ring_svg(40, front=False)}" fill="none" stroke="#0B3A6E" stroke-opacity="{RING_BACK}" stroke-width="{RING_HALF * 80:.2f}"/>
    <path d="{w_svg_path(40)}" fill="#fff"/>
    <path d="{w_ring_svg(40, front=True)}" fill="none" stroke="#0B3A6E" stroke-opacity="{RING_FRONT}" stroke-width="{RING_HALF * 80:.2f}"/>
  </g>
</svg>
'''


def main():
    (PWA_DIR / "icon.svg").write_text(SVG, encoding="utf-8")
    (PWA_DIR / "favicon.svg").write_text(SVG, encoding="utf-8")

    cache = {}
    for size in (180, 192, 512, 32, 128, 256):
        cache[size] = make_png(size)

    for size, name in ((192, "icon-192.png"), (512, "icon-512.png"), (180, "icon-180.png")):
        (PWA_DIR / name).write_bytes(cache[size])

    for size, name in ((32, "32x32.png"), (128, "128x128.png"), (256, "128x128@2x.png"), (512, "icon.png")):
        (TAURI_DIR / name).write_bytes(cache[size])

    (TAURI_DIR / "icon.ico").write_bytes(make_ico([32, 64, 128, 256]))
    (TAURI_DIR / "icon.icns").write_bytes(make_icns([128, 256, 512]))

    print("已生成图标：")
    for p in sorted(PWA_DIR.iterdir()):
        print("  ", p.relative_to(ROOT), p.stat().st_size, "B")
    for p in sorted(TAURI_DIR.iterdir()):
        print("  ", p.relative_to(ROOT), p.stat().st_size, "B")


if __name__ == "__main__":
    main()
