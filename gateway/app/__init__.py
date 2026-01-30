"""
POD Gateway Package

A Flask-based gateway for managing AI-generated images with
human-in-the-loop approval and Printify POD publishing.
"""
__version__ = "2.0.0"

from app.factory import create_app

__all__ = ["create_app", "__version__"]
