"""
StaticWaves Forge - Blender Asset Generator
Main script for generating 3D assets from text prompts using AI models
"""

import bpy
import bmesh
import math
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class ProgressReporter:
    """Report progress back to the worker"""

    def __init__(self, job_id: str):
        self.job_id = job_id
        self.current_progress = 0.0

    def update(self, progress: float, message: str):
        """Update progress (0.0 to 1.0)"""
        self.current_progress = progress
        print(f"PROGRESS:{progress:.2f}:{message}", flush=True)

    def log(self, message: str):
        """Log a message"""
        print(f"LOG:{message}", flush=True)

    def error(self, message: str):
        """Log an error"""
        print(f"ERROR:{message}", flush=True)


class AssetGenerator:
    """Generate 3D assets from text prompts"""

    def __init__(self, job_config: Dict):
        self.config = job_config
        self.job_id = job_config['job_id']
        self.prompt = job_config['prompt']
        self.asset_type = job_config.get('asset_type', 'prop')
        self.style = job_config.get('style', 'low-poly')
        self.poly_budget = job_config.get('poly_budget', 10000)
        self.output_dir = Path(job_config.get('output_dir', f'/tmp/{self.job_id}'))
        self.progress = ProgressReporter(self.job_id)

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.progress.log(f"Initialized generator for: {self.prompt}")

    def generate(self) -> Dict:
        """Main generation pipeline"""
        try:
            self.progress.update(0.0, "Starting generation")

            # Clear the scene
            self._clear_scene()
            self.progress.update(0.05, "Scene cleared")

            # Generate base mesh using AI
            mesh_obj = self._generate_base_mesh()
            self.progress.update(0.25, "Base mesh generated")

            # Process and optimize mesh
            self._process_mesh(mesh_obj)
            self.progress.update(0.40, "Mesh optimized")

            # UV unwrap
            self._unwrap_uv(mesh_obj)
            self.progress.update(0.50, "UV unwrapped")

            # Add rigging if requested
            if self.config.get('include_rig', False):
                self._add_rig(mesh_obj)
                self.progress.update(0.65, "Rigging complete")

            # Generate textures
            self._generate_textures(mesh_obj)
            self.progress.update(0.75, "Textures generated")

            # Generate LODs if requested
            if self.config.get('generate_lods', True):
                lod_objects = self._generate_lods(mesh_obj)
                self.progress.update(0.85, "LODs generated")

            # Export to requested formats
            output_files = self._export_assets(mesh_obj)
            self.progress.update(0.95, "Assets exported")

            # Generate metadata
            metadata = self._generate_metadata(mesh_obj, output_files)
            self.progress.update(1.0, "Generation complete")

            return {
                'status': 'success',
                'output_files': output_files,
                'metadata': metadata
            }

        except Exception as e:
            self.progress.error(f"Generation failed: {str(e)}")
            raise

    def _clear_scene(self):
        """Clear all objects from the scene"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        # Remove orphan data
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)

    def _generate_base_mesh(self) -> bpy.types.Object:
        """
        Generate base mesh from prompt using AI
        In production, this would call Shap-E or Point-E
        For now, we'll generate procedural meshes based on asset type
        """
        self.progress.log(f"Generating {self.asset_type} mesh for: {self.prompt}")

        # Select generation method based on asset type
        generators = {
            'prop': self._generate_prop,
            'weapon': self._generate_weapon,
            'character': self._generate_character,
            'creature': self._generate_creature,
            'building': self._generate_building,
            'vehicle': self._generate_vehicle,
            'environment': self._generate_environment,
        }

        generator = generators.get(self.asset_type, self._generate_prop)
        return generator()

    def _generate_prop(self) -> bpy.types.Object:
        """Generate a prop object"""
        # Create a basic mesh based on style
        if self.style == 'low-poly':
            bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
        else:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))

        obj = bpy.context.active_object
        obj.name = f"prop_{self.job_id[:8]}"

        # Add some variation based on prompt keywords
        self._apply_prompt_modifiers(obj)

        return obj

    def _generate_weapon(self) -> bpy.types.Object:
        """Generate a weapon"""
        # Create a sword-like shape
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0, 0, 1))
        handle = bpy.context.active_object
        handle.scale = (1, 1, 5)

        bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0, 0, 2.5))
        blade = bpy.context.active_object
        blade.scale = (0.5, 3, 5)

        # Join objects
        bpy.ops.object.select_all(action='DESELECT')
        handle.select_set(True)
        blade.select_set(True)
        bpy.context.view_layer.objects.active = blade
        bpy.ops.object.join()

        weapon = bpy.context.active_object
        weapon.name = f"weapon_{self.job_id[:8]}"

        return weapon

    def _generate_character(self) -> bpy.types.Object:
        """Generate a character"""
        # Create basic humanoid shape
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0, 0, 1.5))
        head = bpy.context.active_object

        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.8))
        body = bpy.context.active_object
        body.scale = (0.6, 0.3, 0.8)

        # Join objects
        bpy.ops.object.select_all(action='DESELECT')
        head.select_set(True)
        body.select_set(True)
        bpy.context.view_layer.objects.active = body
        bpy.ops.object.join()

        character = bpy.context.active_object
        character.name = f"character_{self.job_id[:8]}"

        return character

    def _generate_creature(self) -> bpy.types.Object:
        """Generate a creature"""
        # Create organic shape
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=(0, 0, 0))
        obj = bpy.context.active_object
        obj.name = f"creature_{self.job_id[:8]}"

        # Add some organic deformation
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subdivision"].levels = 1

        return obj

    def _generate_building(self) -> bpy.types.Object:
        """Generate a building"""
        bpy.ops.mesh.primitive_cube_add(size=4, location=(0, 0, 2))
        obj = bpy.context.active_object
        obj.scale = (2, 2, 4)
        obj.name = f"building_{self.job_id[:8]}"

        return obj

    def _generate_vehicle(self) -> bpy.types.Object:
        """Generate a vehicle"""
        # Create simple car-like shape
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0.5))
        obj = bpy.context.active_object
        obj.scale = (1.5, 3, 0.8)
        obj.name = f"vehicle_{self.job_id[:8]}"

        return obj

    def _generate_environment(self) -> bpy.types.Object:
        """Generate an environment piece"""
        bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
        obj = bpy.context.active_object

        # Add subdivision for terrain
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subdivision"].levels = 2

        obj.name = f"environment_{self.job_id[:8]}"

        return obj

    def _apply_prompt_modifiers(self, obj: bpy.types.Object):
        """Apply modifiers based on prompt keywords"""
        prompt_lower = self.prompt.lower()

        # Check for style keywords
        if 'smooth' in prompt_lower or 'curved' in prompt_lower:
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers["Subdivision"].levels = 2

        if 'angular' in prompt_lower or 'sharp' in prompt_lower:
            bpy.ops.object.modifier_add(type='EDGE_SPLIT')

        if 'detailed' in prompt_lower:
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers["Subdivision"].levels = 3

    def _process_mesh(self, obj: bpy.types.Object):
        """Process and optimize mesh"""
        self.progress.log("Processing mesh")

        # Apply all modifiers
        bpy.context.view_layer.objects.active = obj
        for modifier in obj.modifiers:
            try:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            except:
                pass

        # Optimize to poly budget
        poly_count = len(obj.data.polygons)

        if poly_count > self.poly_budget:
            # Add decimate modifier
            ratio = self.poly_budget / poly_count
            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.object.modifiers["Decimate"].ratio = ratio
            bpy.ops.object.modifier_apply(modifier="Decimate")

            self.progress.log(f"Decimated from {poly_count} to ~{self.poly_budget} polys")

        # Clean up mesh
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

    def _unwrap_uv(self, obj: bpy.types.Object):
        """Unwrap UV coordinates"""
        self.progress.log("Unwrapping UVs")

        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        # Smart UV project
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)

        bpy.ops.object.mode_set(mode='OBJECT')

    def _add_rig(self, obj: bpy.types.Object):
        """Add rigging to the mesh"""
        self.progress.log("Adding rig")

        # Create a simple armature
        bpy.ops.object.armature_add(location=(0, 0, 0))
        armature = bpy.context.active_object
        armature.name = f"armature_{self.job_id[:8]}"

        # Parent mesh to armature
        obj.select_set(True)
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    def _generate_textures(self, obj: bpy.types.Object):
        """Generate textures for the mesh"""
        self.progress.log("Generating textures")

        # Create material
        mat = bpy.data.materials.new(name=f"mat_{self.job_id[:8]}")
        mat.use_nodes = True

        # Clear default nodes
        mat.node_tree.nodes.clear()

        # Add Principled BSDF
        bsdf = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')

        # Add Material Output
        output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')

        # Link nodes
        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

        # Set some default colors based on asset type
        if self.asset_type == 'weapon':
            bsdf.inputs['Base Color'].default_value = (0.7, 0.7, 0.8, 1.0)  # Metallic gray
            bsdf.inputs['Metallic'].default_value = 0.8
        elif self.asset_type == 'creature':
            bsdf.inputs['Base Color'].default_value = (0.3, 0.6, 0.3, 1.0)  # Green
        else:
            bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)  # White

        # Assign material to object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

    def _generate_lods(self, obj: bpy.types.Object) -> List[bpy.types.Object]:
        """Generate LOD chain"""
        self.progress.log("Generating LODs")

        lods = []
        lod_ratios = [0.5, 0.25, 0.1]  # LOD1: 50%, LOD2: 25%, LOD3: 10%

        for i, ratio in enumerate(lod_ratios):
            # Duplicate object
            lod = obj.copy()
            lod.data = obj.data.copy()
            lod.name = f"{obj.name}_LOD{i+1}"
            bpy.context.collection.objects.link(lod)

            # Decimate
            bpy.context.view_layer.objects.active = lod
            bpy.ops.object.modifier_add(type='DECIMATE')
            lod.modifiers["Decimate"].ratio = ratio
            bpy.ops.object.modifier_apply(modifier="Decimate")

            lods.append(lod)

        return lods

    def _export_assets(self, obj: bpy.types.Object) -> Dict[str, str]:
        """Export assets to requested formats"""
        self.progress.log("Exporting assets")

        output_files = {}
        export_formats = self.config.get('export_formats', ['glb'])

        # Select only the main object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        for fmt in export_formats:
            output_path = self.output_dir / f"asset.{fmt}"

            if fmt == 'glb':
                bpy.ops.export_scene.gltf(
                    filepath=str(output_path),
                    use_selection=True,
                    export_format='GLB'
                )
            elif fmt == 'fbx':
                bpy.ops.export_scene.fbx(
                    filepath=str(output_path),
                    use_selection=True
                )
            elif fmt == 'obj':
                bpy.ops.export_scene.obj(
                    filepath=str(output_path),
                    use_selection=True
                )
            elif fmt == 'gltf':
                bpy.ops.export_scene.gltf(
                    filepath=str(output_path),
                    use_selection=True,
                    export_format='GLTF_SEPARATE'
                )

            output_files[fmt] = str(output_path)
            self.progress.log(f"Exported {fmt.upper()}")

        return output_files

    def _generate_metadata(self, obj: bpy.types.Object, output_files: Dict) -> Dict:
        """Generate metadata for the asset"""
        # Calculate mesh stats
        poly_count = len(obj.data.polygons)
        vertex_count = len(obj.data.vertices)

        # Calculate file sizes
        file_sizes = {}
        for fmt, path in output_files.items():
            if os.path.exists(path):
                size_mb = os.path.getsize(path) / (1024 * 1024)
                file_sizes[fmt] = round(size_mb, 2)

        metadata = {
            'asset_id': self.job_id,
            'name': obj.name,
            'prompt': self.prompt,
            'asset_type': self.asset_type,
            'style': self.style,
            'poly_count': poly_count,
            'vertex_count': vertex_count,
            'has_rig': self.config.get('include_rig', False),
            'has_lods': self.config.get('generate_lods', True),
            'export_formats': list(output_files.keys()),
            'file_sizes_mb': file_sizes,
            'dimensions': {
                'x': obj.dimensions.x,
                'y': obj.dimensions.y,
                'z': obj.dimensions.z
            }
        }

        # Save metadata to file
        metadata_path = self.output_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return metadata


def main():
    """Main entry point"""
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("ERROR:No job config provided")
        sys.exit(1)

    config_path = sys.argv[-1]

    # Load job configuration
    with open(config_path, 'r') as f:
        job_config = json.load(f)

    # Generate asset
    generator = AssetGenerator(job_config)
    result = generator.generate()

    # Write result
    result_path = Path(job_config['output_dir']) / 'result.json'
    with open(result_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"SUCCESS:{result_path}")


if __name__ == "__main__":
    main()
