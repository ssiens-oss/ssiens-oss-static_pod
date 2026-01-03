"""
StaticWaves Forge - AI Model Integration
Integration with Shap-E, Point-E, and other AI models for 3D generation
"""

import os
import torch
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import trimesh

class AIModelGenerator:
    """Generate 3D meshes using AI models"""

    def __init__(self, cache_dir: str = "/workspace/models"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        # Lazy load models
        self.shap_e_model = None
        self.point_e_model = None

    def generate_from_text(
        self,
        prompt: str,
        method: str = "shap-e",
        guidance_scale: float = 15.0,
        num_inference_steps: int = 64
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate 3D mesh from text prompt

        Args:
            prompt: Text description of the 3D asset
            method: "shap-e" or "point-e"
            guidance_scale: How closely to follow the prompt
            num_inference_steps: Quality/speed tradeoff

        Returns:
            vertices, faces: Mesh data as numpy arrays
        """
        if method == "shap-e":
            return self._generate_shap_e(prompt, guidance_scale, num_inference_steps)
        elif method == "point-e":
            return self._generate_point_e(prompt, guidance_scale, num_inference_steps)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _generate_shap_e(
        self,
        prompt: str,
        guidance_scale: float,
        num_inference_steps: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Generate using Shap-E (OpenAI's text-to-3D model)"""
        try:
            from shap_e.diffusion.sample import sample_latents
            from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
            from shap_e.models.download import load_model, load_config
            from shap_e.util.notebooks import decode_latent_mesh

            # Load model (lazy)
            if self.shap_e_model is None:
                print("Loading Shap-E model...")
                self.shap_e_model = load_model('transmitter', device=self.device)
                self.shap_e_diffusion = diffusion_from_config(load_config('diffusion'))

            # Generate latent
            print(f"Generating latent for: {prompt}")
            latents = sample_latents(
                batch_size=1,
                model=self.shap_e_model,
                diffusion=self.shap_e_diffusion,
                guidance_scale=guidance_scale,
                model_kwargs=dict(texts=[prompt]),
                progress=True,
                clip_denoised=True,
                use_fp16=True,
                use_karras=True,
                karras_steps=num_inference_steps,
                sigma_min=1e-3,
                sigma_max=160,
                s_churn=0,
            )

            # Decode to mesh
            print("Decoding latent to mesh...")
            mesh = decode_latent_mesh(self.shap_e_model, latents[0]).tri_mesh()

            vertices = np.array(mesh.verts)
            faces = np.array(mesh.faces)

            print(f"Generated mesh: {len(vertices)} vertices, {len(faces)} faces")
            return vertices, faces

        except ImportError:
            print("WARNING: Shap-E not installed. Install with: pip install shap-e")
            return self._generate_fallback(prompt)
        except Exception as e:
            print(f"ERROR: Shap-E generation failed: {e}")
            return self._generate_fallback(prompt)

    def _generate_point_e(
        self,
        prompt: str,
        guidance_scale: float,
        num_inference_steps: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Generate using Point-E (OpenAI's text-to-point-cloud model)"""
        try:
            from point_e.diffusion.configs import DIFFUSION_CONFIGS, diffusion_from_config
            from point_e.diffusion.sampler import PointCloudSampler
            from point_e.models.download import load_checkpoint
            from point_e.models.configs import MODEL_CONFIGS, model_from_config
            from point_e.util.plotting import plot_point_cloud
            from point_e.util.pc_to_mesh import marching_cubes_mesh

            # Load model (lazy)
            if self.point_e_model is None:
                print("Loading Point-E model...")
                base_name = 'base40M-textvec'
                upsampler_name = 'upsample'

                self.point_e_base = model_from_config(MODEL_CONFIGS[base_name], self.device)
                self.point_e_base.load_state_dict(load_checkpoint(base_name, self.device))

                self.point_e_sampler = PointCloudSampler(
                    device=self.device,
                    models=[self.point_e_base],
                    diffusions=[
                        diffusion_from_config(DIFFUSION_CONFIGS[base_name]),
                    ],
                    num_points=[1024],
                    aux_channels=['R', 'G', 'B'],
                    guidance_scale=[guidance_scale],
                )

            # Generate point cloud
            print(f"Generating point cloud for: {prompt}")
            samples = None
            for x in self.point_e_sampler.sample_batch_progressive(
                batch_size=1,
                model_kwargs=dict(texts=[prompt]),
            ):
                samples = x

            # Convert point cloud to mesh using marching cubes
            print("Converting point cloud to mesh...")
            mesh = marching_cubes_mesh(
                pc=samples[0],
                model=self.point_e_base,
                grid_size=64,
            )

            vertices = np.array(mesh.verts)
            faces = np.array(mesh.faces)

            print(f"Generated mesh: {len(vertices)} vertices, {len(faces)} faces")
            return vertices, faces

        except ImportError:
            print("WARNING: Point-E not installed. Install with: pip install point-e")
            return self._generate_fallback(prompt)
        except Exception as e:
            print(f"ERROR: Point-E generation failed: {e}")
            return self._generate_fallback(prompt)

    def _generate_fallback(self, prompt: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fallback: Generate a simple procedural mesh
        This is used when AI models are not available or fail
        """
        print("Using fallback procedural generation")

        # Create a simple cube as fallback
        mesh = trimesh.creation.box(extents=[2, 2, 2])

        vertices = np.array(mesh.vertices)
        faces = np.array(mesh.faces)

        return vertices, faces

    def save_mesh(
        self,
        vertices: np.ndarray,
        faces: np.ndarray,
        output_path: str,
        format: str = "obj"
    ):
        """Save mesh to file"""
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

        if format == "obj":
            mesh.export(output_path)
        elif format == "ply":
            mesh.export(output_path)
        elif format == "stl":
            mesh.export(output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

        print(f"Saved mesh to: {output_path}")


def test_generation():
    """Test AI generation"""
    generator = AIModelGenerator()

    prompts = [
        "a red apple",
        "a wooden chair",
        "a fantasy sword",
    ]

    for prompt in prompts:
        print(f"\n{'='*60}")
        print(f"Generating: {prompt}")
        print('='*60)

        vertices, faces = generator.generate_from_text(
            prompt=prompt,
            method="shap-e",
            guidance_scale=15.0,
            num_inference_steps=64
        )

        output_path = f"/tmp/test_{prompt.replace(' ', '_')}.obj"
        generator.save_mesh(vertices, faces, output_path)

        print(f"Saved to: {output_path}")


if __name__ == "__main__":
    test_generation()
