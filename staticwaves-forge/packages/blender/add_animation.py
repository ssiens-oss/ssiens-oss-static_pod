#!/usr/bin/env python3
"""
StaticWaves Forge - Animation Generator
Adds procedural animations to rigged characters
"""

import bpy
import sys
import math
import random

def create_idle_animation(armature, duration=60):
    """Create a subtle idle/breathing animation"""
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = duration

    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    # Animate spine for breathing
    if 'Spine' in armature.pose.bones:
        spine = armature.pose.bones['Spine']

        # Frame 1
        scene.frame_set(1)
        spine.scale = (1, 1, 1)
        spine.keyframe_insert(data_path="scale", frame=1)

        # Frame 30 (inhale)
        scene.frame_set(30)
        spine.scale = (1.02, 1.02, 1.05)
        spine.keyframe_insert(data_path="scale", frame=30)

        # Frame 60 (exhale)
        scene.frame_set(60)
        spine.scale = (1, 1, 1)
        spine.keyframe_insert(data_path="scale", frame=60)

    # Slight head movement
    if 'Head' in armature.pose.bones:
        head = armature.pose.bones['Head']

        scene.frame_set(1)
        head.rotation_euler = (0, 0, 0)
        head.keyframe_insert(data_path="rotation_euler", frame=1)

        scene.frame_set(30)
        head.rotation_euler = (math.radians(2), 0, math.radians(1))
        head.keyframe_insert(data_path="rotation_euler", frame=30)

        scene.frame_set(60)
        head.rotation_euler = (0, 0, 0)
        head.keyframe_insert(data_path="rotation_euler", frame=60)

    bpy.ops.object.mode_set(mode='OBJECT')
    print("✅ Idle animation created")

def create_walk_cycle(armature, duration=24):
    """Create a basic walk cycle"""
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = duration

    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    frames = [1, 7, 13, 19, 24]

    # Animate legs
    for side in ['L', 'R']:
        upper_leg_name = f'UpperLeg.{side}'
        lower_leg_name = f'LowerLeg.{side}'

        if upper_leg_name not in armature.pose.bones:
            continue

        upper_leg = armature.pose.bones[upper_leg_name]
        lower_leg = armature.pose.bones[lower_leg_name]

        # Opposite phase for left and right
        offset = 0 if side == 'L' else 12

        for i, frame in enumerate(frames):
            scene.frame_set(frame)

            # Simple forward/back swing
            angle = math.radians(30 * math.sin((frame + offset) * math.pi / 12))
            upper_leg.rotation_euler = (angle, 0, 0)
            upper_leg.keyframe_insert(data_path="rotation_euler", frame=frame)

            # Knee bend
            knee_angle = abs(math.radians(20 * math.sin((frame + offset) * math.pi / 12)))
            lower_leg.rotation_euler = (knee_angle, 0, 0)
            lower_leg.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Animate arms (opposite to legs)
    for side in ['L', 'R']:
        upper_arm_name = f'UpperArm.{side}'

        if upper_arm_name not in armature.pose.bones:
            continue

        upper_arm = armature.pose.bones[upper_arm_name]

        # Opposite phase to legs
        offset = 12 if side == 'L' else 0

        for frame in frames:
            scene.frame_set(frame)
            angle = math.radians(20 * math.sin((frame + offset) * math.pi / 12))
            upper_arm.rotation_euler = (angle, 0, 0)
            upper_arm.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Add slight spine rotation
    if 'Spine' in armature.pose.bones:
        spine = armature.pose.bones['Spine']
        for frame in frames:
            scene.frame_set(frame)
            angle = math.radians(3 * math.sin(frame * math.pi / 12))
            spine.rotation_euler = (0, 0, angle)
            spine.keyframe_insert(data_path="rotation_euler", frame=frame)

    bpy.ops.object.mode_set(mode='OBJECT')
    print("✅ Walk cycle created")

def create_jump_animation(armature, duration=30):
    """Create a simple jump animation"""
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = duration

    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    if 'Root' in armature.pose.bones:
        root = armature.pose.bones['Root']

        # Crouch
        scene.frame_set(1)
        root.location = (0, 0, 0)
        root.keyframe_insert(data_path="location", frame=1)

        scene.frame_set(8)
        root.location = (0, 0, -0.3)
        root.keyframe_insert(data_path="location", frame=8)

        # Jump
        scene.frame_set(15)
        root.location = (0, 0, 1.5)
        root.keyframe_insert(data_path="location", frame=15)

        # Land
        scene.frame_set(24)
        root.location = (0, 0, -0.2)
        root.keyframe_insert(data_path="location", frame=24)

        scene.frame_set(30)
        root.location = (0, 0, 0)
        root.keyframe_insert(data_path="location", frame=30)

    bpy.ops.object.mode_set(mode='OBJECT')
    print("✅ Jump animation created")

def bake_animation(armature, action_name):
    """Bake the animation for export"""
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    bpy.ops.nla.bake(
        frame_start=bpy.context.scene.frame_start,
        frame_end=bpy.context.scene.frame_end,
        visual_keying=True,
        clear_constraints=False,
        use_current_action=True,
        bake_types={'POSE'}
    )

    if armature.animation_data and armature.animation_data.action:
        armature.animation_data.action.name = action_name

    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"✅ Animation baked: {action_name}")

def main():
    """Main entry point"""
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    anim_type = argv[0] if len(argv) > 0 else "idle"
    duration = int(argv[1]) if len(argv) > 1 else 60

    # Find armature
    armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
    if not armatures:
        print("❌ No armature found in scene")
        sys.exit(1)

    armature = armatures[0]
    print(f"🎬 Creating {anim_type} animation for {armature.name}")

    if anim_type == "idle":
        create_idle_animation(armature, duration)
        bake_animation(armature, "Idle")
    elif anim_type == "walk":
        create_walk_cycle(armature, duration)
        bake_animation(armature, "Walk")
    elif anim_type == "jump":
        create_jump_animation(armature, duration)
        bake_animation(armature, "Jump")
    else:
        print(f"❌ Unknown animation type: {anim_type}")
        sys.exit(1)

    print("✅ Animation complete")

if __name__ == "__main__":
    main()
