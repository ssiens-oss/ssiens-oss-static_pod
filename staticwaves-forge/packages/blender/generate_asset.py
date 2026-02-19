#!/usr/bin/env python3
"""
StaticWaves Forge - Core Asset Generator
Generates procedural 3D assets with deterministic seeds
"""

import bpy
import sys
import random
import math
import os
from pathlib import Path

def clear_scene():
    """Remove all default objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def generate_creature(seed, style="low-poly"):
    """Generate a simple creature asset"""
    random.seed(seed)

    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=1,
        segments=12 if style == "low-poly" else 32,
        ring_count=8 if style == "low-poly" else 16,
        location=(0, 0, 1)
    )
    body = bpy.context.active_object
    body.name = "Body"
    body.scale = (1, 1.2, 1.5)

    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.6,
        segments=12 if style == "low-poly" else 32,
        ring_count=8 if style == "low-poly" else 16,
        location=(0, 0, 2.8)
    )
    head = bpy.context.active_object
    head.name = "Head"

    # Eyes
    for x in [-0.3, 0.3]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.15,
            segments=8,
            ring_count=6,
            location=(x, -0.4, 3.0)
        )
        eye = bpy.context.active_object
        eye.name = f"Eye_{x}"

    # Limbs (simple cylinders)
    for side in [-1, 1]:
        # Arms
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.2,
            depth=1.5,
            location=(side * 0.8, 0, 1.2),
            rotation=(0, math.radians(30 * side), 0)
        )
        arm = bpy.context.active_object
        arm.name = f"Arm_{side}"

        # Legs
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.25,
            depth=1.8,
            location=(side * 0.5, 0, 0.1),
            rotation=(0, 0, 0)
        )
        leg = bpy.context.active_object
        leg.name = f"Leg_{side}"

    # Apply smooth shading to all
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.shade_smooth()

    return body

def generate_prop(seed, prop_type="crate"):
    """Generate a simple prop asset"""
    random.seed(seed)

    if prop_type == "crate":
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
        obj = bpy.context.active_object
        obj.name = "Crate"
        obj.scale = (
            random.uniform(0.8, 1.2),
            random.uniform(0.8, 1.2),
            random.uniform(0.8, 1.2)
        )

    elif prop_type == "barrel":
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.5,
            depth=1.5,
            location=(0, 0, 0.75)
        )
        obj = bpy.context.active_object
        obj.name = "Barrel"

    elif prop_type == "rock":
        bpy.ops.mesh.primitive_ico_sphere_add(
            radius=0.8,
            subdivisions=2,
            location=(0, 0, 0)
        )
        obj = bpy.context.active_object
        obj.name = "Rock"

        # Add slight randomization to vertices
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.transform.vertex_random(offset=0.2, seed=seed)
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.shade_smooth()
    return obj

def generate_weapon(seed, weapon_type="sword"):
    """Generate a simple weapon asset"""
    random.seed(seed)

    if weapon_type == "sword":
        # Blade
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0, 0, 0.5)
        )
        blade = bpy.context.active_object
        blade.name = "Blade"
        blade.scale = (0.1, 0.05, 1.5)

        # Handle
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.08,
            depth=0.4,
            location=(0, 0, -0.5)
        )
        handle = bpy.context.active_object
        handle.name = "Handle"

        # Guard
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0, 0, -0.2)
        )
        guard = bpy.context.active_object
        guard.name = "Guard"
        guard.scale = (0.5, 0.05, 0.05)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.shade_smooth()
    return blade

def add_simple_material(obj, color=(0.5, 0.5, 0.5, 1.0)):
    """Add a simple material to object"""
    mat = bpy.data.materials.new(name=f"Material_{obj.name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = 0.2
    bsdf.inputs["Roughness"].default_value = 0.7

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def export_asset(output_path, format="glb"):
    """Export the generated asset"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if format == "glb" or format == "gltf":
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            export_format='GLB' if format == "glb" else 'GLTF_SEPARATE',
            export_materials='EXPORT',
            export_texcoords=True,
            export_normals=True,
            export_apply=True
        )
    elif format == "fbx":
        bpy.ops.export_scene.fbx(
            filepath=output_path,
            use_selection=False,
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_ALL',
            axis_forward='-Z',
            axis_up='Y'
        )
    elif format == "obj":
        bpy.ops.export_scene.obj(
            filepath=output_path,
            use_selection=False,
            use_materials=True,
            use_normals=True,
            use_uvs=True
        )

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: blender --background --python generate_asset.py -- <seed> <type> <output>")
        sys.exit(1)

    # Parse arguments (after --)
    argv = sys.argv[sys.argv.index("--") + 1:]
    seed = int(argv[0]) if len(argv) > 0 else 42
    asset_type = argv[1] if len(argv) > 1 else "creature"
    output_path = argv[2] if len(argv) > 2 else "/output/asset.glb"
    style = argv[3] if len(argv) > 3 else "low-poly"

    print(f"🔥 Generating {asset_type} with seed {seed}")

    # Clear default scene
    clear_scene()

    # Generate based on type
    if asset_type == "creature":
        obj = generate_creature(seed, style)
    elif asset_type == "prop":
        obj = generate_prop(seed, "crate")
    elif asset_type == "weapon":
        obj = generate_weapon(seed, "sword")
    else:
        obj = generate_prop(seed, asset_type)

    # Add material
    add_simple_material(obj, color=(
        random.uniform(0.3, 0.9),
        random.uniform(0.3, 0.9),
        random.uniform(0.3, 0.9),
        1.0
    ))

    # Export
    export_format = output_path.split('.')[-1]
    export_asset(output_path, export_format)

    print(f"✅ Asset exported to {output_path}")

if __name__ == "__main__":
    main()
