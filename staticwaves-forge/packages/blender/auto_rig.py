#!/usr/bin/env python3
"""
StaticWaves Forge - Auto-Rigging System
Automatically creates bone rigs for humanoid and creature assets
"""

import bpy
import sys
import math
from mathutils import Vector

def create_humanoid_rig(name="Armature"):
    """Create a basic humanoid armature"""
    bpy.ops.object.armature_add(location=(0, 0, 0))
    armature = bpy.context.active_object
    armature.name = name
    armature.show_in_front = True

    bpy.ops.object.mode_set(mode='EDIT')
    bones = armature.data.edit_bones

    # Remove default bone
    bones.remove(bones[0])

    # Root
    root = bones.new('Root')
    root.head = Vector((0, 0, 0))
    root.tail = Vector((0, 0, 0.3))

    # Spine chain
    spine = bones.new('Spine')
    spine.head = Vector((0, 0, 0.3))
    spine.tail = Vector((0, 0, 1.0))
    spine.parent = root

    spine2 = bones.new('Spine2')
    spine2.head = Vector((0, 0, 1.0))
    spine2.tail = Vector((0, 0, 1.5))
    spine2.parent = spine

    # Neck and Head
    neck = bones.new('Neck')
    neck.head = Vector((0, 0, 1.5))
    neck.tail = Vector((0, 0, 2.0))
    neck.parent = spine2

    head = bones.new('Head')
    head.head = Vector((0, 0, 2.0))
    head.tail = Vector((0, 0, 2.8))
    head.parent = neck

    # Arms (left and right)
    for side, x_sign in [('L', 1), ('R', -1)]:
        # Shoulder
        shoulder = bones.new(f'Shoulder.{side}')
        shoulder.head = Vector((x_sign * 0.2, 0, 1.4))
        shoulder.tail = Vector((x_sign * 0.5, 0, 1.4))
        shoulder.parent = spine2

        # Upper arm
        upper_arm = bones.new(f'UpperArm.{side}')
        upper_arm.head = Vector((x_sign * 0.5, 0, 1.4))
        upper_arm.tail = Vector((x_sign * 0.9, 0, 1.0))
        upper_arm.parent = shoulder

        # Lower arm
        lower_arm = bones.new(f'LowerArm.{side}')
        lower_arm.head = Vector((x_sign * 0.9, 0, 1.0))
        lower_arm.tail = Vector((x_sign * 1.3, 0, 0.7))
        lower_arm.parent = upper_arm

        # Hand
        hand = bones.new(f'Hand.{side}')
        hand.head = Vector((x_sign * 1.3, 0, 0.7))
        hand.tail = Vector((x_sign * 1.5, 0, 0.7))
        hand.parent = lower_arm

    # Legs (left and right)
    for side, x_sign in [('L', 1), ('R', -1)]:
        # Upper leg
        upper_leg = bones.new(f'UpperLeg.{side}')
        upper_leg.head = Vector((x_sign * 0.3, 0, 0.3))
        upper_leg.tail = Vector((x_sign * 0.3, 0, -0.5))
        upper_leg.parent = root

        # Lower leg
        lower_leg = bones.new(f'LowerLeg.{side}')
        lower_leg.head = Vector((x_sign * 0.3, 0, -0.5))
        lower_leg.tail = Vector((x_sign * 0.3, 0, -1.3))
        lower_leg.parent = upper_leg

        # Foot
        foot = bones.new(f'Foot.{side}')
        foot.head = Vector((x_sign * 0.3, 0, -1.3))
        foot.tail = Vector((x_sign * 0.3, 0.3, -1.5))
        foot.parent = lower_leg

    bpy.ops.object.mode_set(mode='OBJECT')
    return armature

def auto_skin_weights(mesh_obj, armature):
    """Automatically assign skin weights using Blender's auto weights"""
    # Select mesh and armature
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature

    # Parent with automatic weights
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    print(f"✅ Auto-skinned {mesh_obj.name} to {armature.name}")

def create_simple_rig_for_mesh(mesh_name=None):
    """Create and bind a simple rig to the active mesh"""
    if mesh_name:
        mesh_obj = bpy.data.objects.get(mesh_name)
    else:
        mesh_obj = bpy.context.active_object

    if not mesh_obj or mesh_obj.type != 'MESH':
        print("❌ No mesh selected or found")
        return None

    print(f"🦴 Creating rig for {mesh_obj.name}")

    # Create armature
    armature = create_humanoid_rig(f"{mesh_obj.name}_Armature")

    # Auto-skin
    auto_skin_weights(mesh_obj, armature)

    return armature

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        # Try to rig the first mesh in scene
        meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        if meshes:
            create_simple_rig_for_mesh(meshes[0].name)
        else:
            print("❌ No meshes found to rig")
            sys.exit(1)
    else:
        argv = sys.argv[sys.argv.index("--") + 1:]
        mesh_name = argv[0] if len(argv) > 0 else None
        create_simple_rig_for_mesh(mesh_name)

    print("✅ Rigging complete")

if __name__ == "__main__":
    main()
