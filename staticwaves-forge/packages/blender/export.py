#!/usr/bin/env python3
"""
StaticWaves Forge - Multi-Format Exporter
Exports assets in engine-ready formats (Unity, Unreal, Roblox)
"""

import bpy
import sys
import os
from pathlib import Path

def export_unity(output_path, include_animations=True):
    """Export asset for Unity (FBX format)"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.export_scene.fbx(
        filepath=output_path,
        use_selection=False,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        bake_anim=include_animations,
        bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=1.0,
        path_mode='COPY',
        embed_textures=True,
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE'
    )
    print(f"✅ Unity export complete: {output_path}")

def export_unreal(output_path, include_animations=True):
    """Export asset for Unreal Engine (FBX format)"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.export_scene.fbx(
        filepath=output_path,
        use_selection=False,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        bake_anim=include_animations,
        bake_anim_use_all_actions=True,
        bake_anim_use_nla_strips=True,
        bake_anim_step=1.0,
        path_mode='COPY',
        embed_textures=True,
        add_leaf_bones=False,  # Unreal-specific
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        use_mesh_modifiers=True
    )
    print(f"✅ Unreal export complete: {output_path}")

def export_roblox(output_path):
    """Export asset for Roblox (FBX format with specific settings)"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Roblox prefers Y-up, -Z forward
    bpy.ops.export_scene.fbx(
        filepath=output_path,
        use_selection=False,
        global_scale=0.01,  # Roblox uses studs (smaller units)
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        bake_anim=True,
        bake_anim_use_all_actions=True,
        path_mode='COPY',
        embed_textures=True,
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE'
    )
    print(f"✅ Roblox export complete: {output_path}")

def export_glb(output_path, include_animations=True):
    """Export as GLB (universal format)"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_materials='EXPORT',
        export_texcoords=True,
        export_normals=True,
        export_draco_mesh_compression_enable=False,
        export_apply=True,
        export_animations=include_animations,
        export_frame_range=True,
        export_force_sampling=True,
        export_yup=True
    )
    print(f"✅ GLB export complete: {output_path}")

def export_obj(output_path):
    """Export as OBJ (static mesh only)"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.export_scene.obj(
        filepath=output_path,
        use_selection=False,
        use_materials=True,
        use_normals=True,
        use_uvs=True,
        use_triangles=True,
        use_mesh_modifiers=True,
        axis_forward='-Z',
        axis_up='Y',
        global_scale=1.0,
        path_mode='COPY'
    )
    print(f"✅ OBJ export complete: {output_path}")

def export_all_formats(base_path, name="asset", include_animations=True):
    """Export asset in all formats"""
    base_dir = Path(base_path)
    base_dir.mkdir(parents=True, exist_ok=True)

    formats = {
        'unity': ('fbx', export_unity),
        'unreal': ('fbx', export_unreal),
        'roblox': ('fbx', export_roblox),
        'glb': ('glb', export_glb),
        'obj': ('obj', export_obj)
    }

    for engine, (ext, export_func) in formats.items():
        output = base_dir / engine / f"{name}.{ext}"
        try:
            if ext == 'obj':
                export_func(str(output))
            else:
                export_func(str(output), include_animations)
        except Exception as e:
            print(f"❌ Failed to export {engine}: {e}")

def main():
    """Main entry point"""
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

    if len(argv) < 1:
        print("Usage: blender --background --python export.py -- <engine> <output_path> [include_animations]")
        print("Engines: unity, unreal, roblox, glb, obj, all")
        sys.exit(1)

    engine = argv[0].lower()
    output_path = argv[1] if len(argv) > 1 else f"/output/{engine}_export.fbx"
    include_animations = argv[2].lower() == 'true' if len(argv) > 2 else True

    print(f"🚀 Exporting for {engine}")

    if engine == "unity":
        export_unity(output_path, include_animations)
    elif engine == "unreal":
        export_unreal(output_path, include_animations)
    elif engine == "roblox":
        export_roblox(output_path)
    elif engine == "glb":
        export_glb(output_path, include_animations)
    elif engine == "obj":
        export_obj(output_path)
    elif engine == "all":
        base_path = argv[1] if len(argv) > 1 else "/output"
        name = argv[2] if len(argv) > 2 else "asset"
        export_all_formats(base_path, name, include_animations)
    else:
        print(f"❌ Unknown engine: {engine}")
        sys.exit(1)

    print("✅ Export complete")

if __name__ == "__main__":
    main()
