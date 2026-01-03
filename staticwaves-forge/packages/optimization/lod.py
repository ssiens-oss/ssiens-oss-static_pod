#!/usr/bin/env python3
"""
StaticWaves Forge - LOD (Level of Detail) Generator
Automatically creates multiple LOD levels for mesh optimization
"""

import bpy
import sys
from pathlib import Path

def create_lod_levels(obj, ratios=[1.0, 0.5, 0.25, 0.1]):
    """
    Create LOD levels for a mesh object

    Args:
        obj: Blender mesh object
        ratios: List of decimation ratios (1.0 = original)

    Returns:
        List of LOD objects
    """
    lod_objects = []

    for i, ratio in enumerate(ratios):
        if i == 0:
            # LOD0 is the original
            obj.name = f"{obj.name}_LOD0"
            lod_objects.append(obj)
        else:
            # Duplicate and decimate
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            # Duplicate
            bpy.ops.object.duplicate()
            lod_obj = bpy.context.active_object
            lod_obj.name = f"{obj.name.replace('_LOD0', '')}_LOD{i}"

            # Add decimate modifier
            decimate = lod_obj.modifiers.new(name="Decimate", type='DECIMATE')
            decimate.ratio = ratio
            decimate.use_collapse_triangulate = True

            # Apply modifier
            bpy.ops.object.modifier_apply(modifier="Decimate")

            # Store polycount info
            polycount = len(lod_obj.data.polygons)
            print(f"  LOD{i}: {polycount} polygons ({ratio*100:.0f}% of original)")

            lod_objects.append(lod_obj)

    return lod_objects

def optimize_mesh(obj, target_poly_count=None, preserve_uvs=True):
    """
    Optimize a single mesh to target polygon count

    Args:
        obj: Blender mesh object
        target_poly_count: Target number of polygons (None = auto)
        preserve_uvs: Preserve UV coordinates during decimation
    """
    if not obj or obj.type != 'MESH':
        print(f"❌ {obj.name} is not a mesh")
        return

    current_poly_count = len(obj.data.polygons)

    if target_poly_count:
        ratio = target_poly_count / current_poly_count
        ratio = max(0.01, min(1.0, ratio))  # Clamp between 1% and 100%
    else:
        # Auto-optimize to reasonable levels
        if current_poly_count > 100000:
            ratio = 0.3
        elif current_poly_count > 50000:
            ratio = 0.5
        elif current_poly_count > 10000:
            ratio = 0.7
        else:
            ratio = 1.0  # Don't decimate if already low-poly

    if ratio < 1.0:
        bpy.context.view_layer.objects.active = obj
        decimate = obj.modifiers.new(name="Decimate", type='DECIMATE')
        decimate.ratio = ratio
        decimate.use_collapse_triangulate = True

        # Apply
        bpy.ops.object.modifier_apply(modifier="Decimate")

        new_poly_count = len(obj.data.polygons)
        print(f"✅ Optimized {obj.name}: {current_poly_count} → {new_poly_count} polygons")
    else:
        print(f"✅ {obj.name} already optimized ({current_poly_count} polygons)")

def remove_doubles(obj, threshold=0.0001):
    """Remove duplicate vertices"""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=threshold)
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"✅ Removed duplicate vertices from {obj.name}")

def triangulate_mesh(obj):
    """Convert all faces to triangles (required for some engines)"""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"✅ Triangulated {obj.name}")

def optimize_scene_for_mobile():
    """Optimize entire scene for mobile/low-end devices"""
    print("📱 Optimizing scene for mobile...")

    meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    for obj in meshes:
        # Remove doubles
        remove_doubles(obj)

        # Triangulate
        triangulate_mesh(obj)

        # Optimize to low poly count
        optimize_mesh(obj, target_poly_count=5000)

def create_standard_lods():
    """Create LOD levels for all meshes in scene"""
    print("🔧 Creating LOD levels...")

    meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    if not meshes:
        print("❌ No meshes found in scene")
        return

    # Standard LOD ratios
    ratios = [1.0, 0.6, 0.3, 0.15]

    for obj in meshes:
        print(f"\nProcessing {obj.name}:")
        lods = create_lod_levels(obj, ratios)
        print(f"✅ Created {len(lods)} LOD levels for {obj.name}")

def main():
    """Main entry point"""
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

    if len(argv) < 1:
        print("Usage: blender --background --python lod.py -- <mode> [options]")
        print("Modes:")
        print("  lod              - Create LOD levels for all meshes")
        print("  optimize         - Optimize meshes to target poly count")
        print("  mobile           - Optimize for mobile devices")
        sys.exit(1)

    mode = argv[0].lower()

    if mode == "lod":
        create_standard_lods()
    elif mode == "optimize":
        target = int(argv[1]) if len(argv) > 1 else None
        meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        for obj in meshes:
            optimize_mesh(obj, target)
    elif mode == "mobile":
        optimize_scene_for_mobile()
    else:
        print(f"❌ Unknown mode: {mode}")
        sys.exit(1)

    print("\n✅ Optimization complete")

if __name__ == "__main__":
    main()
