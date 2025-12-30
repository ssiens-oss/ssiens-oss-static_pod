"""
Configuration management for Claude + ComfyUI Auto Asset System
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class RunPodConfig:
    """RunPod API configuration"""
    api_key: str
    pod_id: str
    pod_ip: str
    comfyui_port: int = 8188

    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("RUNPOD_API_KEY", ""),
            pod_id=os.getenv("RUNPOD_POD_ID", ""),
            pod_ip=os.getenv("RUNPOD_POD_IP", ""),
            comfyui_port=int(os.getenv("COMFYUI_PORT", "8188"))
        )


@dataclass
class ClaudeConfig:
    """Anthropic Claude API configuration"""
    api_key: str
    model: str = "claude-sonnet-4-5-20250929"
    max_tokens: int = 4096

    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929"),
            max_tokens=int(os.getenv("CLAUDE_MAX_TOKENS", "4096"))
        )


@dataclass
class MarketplaceConfig:
    """Marketplace API credentials"""
    gumroad_access_token: str
    itchio_api_key: str

    @classmethod
    def from_env(cls):
        return cls(
            gumroad_access_token=os.getenv("GUMROAD_ACCESS_TOKEN", ""),
            itchio_api_key=os.getenv("ITCHIO_API_KEY", "")
        )


@dataclass
class NotionConfig:
    """Notion API configuration"""
    api_key: str
    database_id: str

    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("NOTION_API_KEY", ""),
            database_id=os.getenv("NOTION_DATABASE_ID", "")
        )


@dataclass
class AssetConfig:
    """Asset generation configuration"""
    workspace_dir: str = "/workspace/icons"
    output_dir: str = "./output"
    archive_dir: str = "./archives"

    @classmethod
    def from_env(cls):
        return cls(
            workspace_dir=os.getenv("WORKSPACE_DIR", "/workspace/icons"),
            output_dir=os.getenv("OUTPUT_DIR", "./output"),
            archive_dir=os.getenv("ARCHIVE_DIR", "./archives")
        )


class Config:
    """Central configuration manager"""

    def __init__(self):
        self.runpod = RunPodConfig.from_env()
        self.claude = ClaudeConfig.from_env()
        self.marketplace = MarketplaceConfig.from_env()
        self.notion = NotionConfig.from_env()
        self.asset = AssetConfig.from_env()

    def validate(self) -> list[str]:
        """Validate required configuration"""
        errors = []

        if not self.runpod.api_key:
            errors.append("RUNPOD_API_KEY not set")
        if not self.runpod.pod_id:
            errors.append("RUNPOD_POD_ID not set")
        if not self.claude.api_key:
            errors.append("ANTHROPIC_API_KEY not set")

        return errors

    def validate_marketplace(self) -> list[str]:
        """Validate marketplace credentials"""
        errors = []

        if not self.marketplace.gumroad_access_token:
            errors.append("GUMROAD_ACCESS_TOKEN not set")
        if not self.marketplace.itchio_api_key:
            errors.append("ITCHIO_API_KEY not set")

        return errors

    def validate_notion(self) -> list[str]:
        """Validate Notion credentials"""
        errors = []

        if not self.notion.api_key:
            errors.append("NOTION_API_KEY not set")
        if not self.notion.database_id:
            errors.append("NOTION_DATABASE_ID not set")

        return errors


# Global config instance
config = Config()
