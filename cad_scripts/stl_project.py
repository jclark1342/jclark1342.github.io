import math
import os
import struct
import sys


def read_binary_stl(path):
    with open(path, "rb") as handle:
        data = handle.read()
    count = struct.unpack("<I", data[80:84])[0]
    triangles = []
    offset = 84
    for _ in range(count):
        if offset + 50 > len(data):
            break
        values = struct.unpack("<12fH", data[offset : offset + 50])
        vertices = [values[3:6], values[6:9], values[9:12]]
        triangles.append(vertices)
        offset += 50
    return triangles


def rotate(point, rx, ry, rz):
    x, y, z = point
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)

    y, z = y * cx - z * sx, y * sx + z * cx
    x, z = x * cy + z * sy, -x * sy + z * cy
    x, y = x * cz - y * sz, x * sz + y * cz
    return x, y, z


def draw_line(img, zbuf, p0, p1, shade):
    width = len(img[0])
    height = len(img)
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    steps = int(max(abs(x1 - x0), abs(y1 - y0), 1))
    for i in range(steps + 1):
        t = i / steps
        x = int(round(x0 + (x1 - x0) * t))
        y = int(round(y0 + (y1 - y0) * t))
        z = z0 + (z1 - z0) * t
        if 0 <= x < width and 0 <= y < height and z >= zbuf[y][x]:
            zbuf[y][x] = z
            img[y][x] = shade


def rasterize(triangles, out_path, angles, size=1400):
    rotated = [[rotate(v, *angles) for v in tri] for tri in triangles]
    points = [v for tri in rotated for v in tri]
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    span = max(max_x - min_x, max_y - min_y)
    margin = size * 0.08
    scale = (size - margin * 2.0) / span

    def project(point):
        x, y, z = point
        return (
            margin + (x - min_x) * scale,
            size - (margin + (y - min_y) * scale),
            z,
        )

    img = [[255 for _ in range(size)] for _ in range(size)]
    zbuf = [[-1e9 for _ in range(size)] for _ in range(size)]

    for tri in rotated:
        projected = [project(v) for v in tri]
        zs = [p[2] for p in projected]
        shade = int(max(30, min(210, 150 - (sum(zs) / 3.0) * 0.8)))
        for i in range(3):
            draw_line(img, zbuf, projected[i], projected[(i + 1) % 3], shade)

    with open(out_path, "wb") as handle:
        handle.write(f"P5\n{size} {size}\n255\n".encode("ascii"))
        handle.write(bytes(value for row in img for value in row))


def main():
    stl_path = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    triangles = read_binary_stl(stl_path)
    views = {
        "front": (math.radians(65), 0, 0),
        "top": (0, 0, 0),
        "side": (math.radians(90), 0, math.radians(90)),
        "iso": (math.radians(60), 0, math.radians(35)),
    }
    for name, angles in views.items():
        rasterize(triangles, os.path.join(out_dir, f"bracelet_{name}.pgm"), angles)


if __name__ == "__main__":
    main()
