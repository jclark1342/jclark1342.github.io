import os
import sys

import bpy
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def bounds_center(obj):
    return obj.matrix_world @ (sum((Vector(corner) for corner in obj.bound_box), Vector()) / 8.0)


def render_view(scene, obj, name, direction, out_dir):
    center = bounds_center(obj)
    dims = obj.dimensions
    radius = max(dims) * 0.9

    camera_data = bpy.data.cameras.new(f"cam_{name}")
    camera = bpy.data.objects.new(f"cam_{name}", camera_data)
    bpy.context.collection.objects.link(camera)

    direction = Vector(direction).normalized()
    camera.location = center + direction * radius * 2.2
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(dims) * 1.25
    camera.data.lens = 55

    scene.camera = camera
    scene.render.filepath = os.path.join(out_dir, f"bracelet_{name}.png")
    bpy.ops.render.render(write_still=True)


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: blender --background --python render_stl_refs.py -- <stl> <out_dir>")

    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    stl_path = argv[0]
    out_dir = argv[1]
    os.makedirs(out_dir, exist_ok=True)

    clear_scene()
    bpy.ops.import_mesh.stl(filepath=stl_path)
    obj = bpy.context.object
    obj.name = "RoyalPopCaseBracelet"
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")

    material = bpy.data.materials.new("yellow_reference")
    material.diffuse_color = (0.9, 0.82, 0.08, 1.0)
    obj.data.materials.append(material)

    bpy.ops.object.light_add(type="AREA", location=(0, -120, 120))
    light = bpy.context.object
    light.data.energy = 500
    light.data.size = 60

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900

    print("dimensions_mm", tuple(round(value, 3) for value in obj.dimensions), flush=True)
    for name, direction in [
        ("front", (0, -1, 0.45)),
        ("top", (0, 0, 1)),
        ("iso", (0.75, -0.85, 0.65)),
    ]:
        render_view(scene, obj, name, direction, out_dir)


if __name__ == "__main__":
    main()
