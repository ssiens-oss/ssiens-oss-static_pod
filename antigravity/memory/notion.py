"""Notion integration for human-readable decision logs."""

import os
import requests
from typing import Optional, Dict, Any, List


def log_decision_to_notion(
    title: str,
    summary: str,
    fields: Optional[Dict[str, Any]] = None,
    database_id: Optional[str] = None,
    api_token: Optional[str] = None,
) -> bool:
    """
    Log a decision to Notion database.

    Args:
        title: Decision title
        summary: Decision summary
        fields: Optional additional fields
        database_id: Notion database ID (uses NOTION_DB_ID env var if not provided)
        api_token: Notion API token (uses NOTION_TOKEN env var if not provided)

    Returns:
        True if successful, False otherwise
    """
    database_id = database_id or os.environ.get("NOTION_DB_ID")
    api_token = api_token or os.environ.get("NOTION_TOKEN")

    if not database_id or not api_token:
        print("Warning: Notion not configured (NOTION_DB_ID and NOTION_TOKEN required)")
        return False

    try:
        url = "https://api.notion.com/v1/pages"

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

        # Build properties
        properties = {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
        }

        # Add additional fields if provided
        if fields:
            for key, value in fields.items():
                if isinstance(value, str):
                    properties[key] = {
                        "rich_text": [
                            {
                                "text": {
                                    "content": value
                                }
                            }
                        ]
                    }
                elif isinstance(value, (int, float)):
                    properties[key] = {
                        "number": value
                    }
                elif isinstance(value, bool):
                    properties[key] = {
                        "checkbox": value
                    }

        # Build children (content blocks)
        children = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": summary
                            }
                        }
                    ]
                }
            }
        ]

        payload = {
            "parent": {
                "database_id": database_id
            },
            "properties": properties,
            "children": children,
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=10,
        )

        response.raise_for_status()
        return True

    except requests.exceptions.RequestException as e:
        print(f"Notion logging failed: {e}")
        return False


def create_notion_database(
    title: str,
    parent_page_id: str,
    api_token: Optional[str] = None,
) -> Optional[str]:
    """
    Create a new Notion database for POD decisions.

    Args:
        title: Database title
        parent_page_id: Parent page ID
        api_token: Notion API token

    Returns:
        Database ID if successful, None otherwise
    """
    api_token = api_token or os.environ.get("NOTION_TOKEN")

    if not api_token:
        print("Warning: NOTION_TOKEN not configured")
        return None

    try:
        url = "https://api.notion.com/v1/databases"

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

        payload = {
            "parent": {
                "type": "page_id",
                "page_id": parent_page_id
            },
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": title
                    }
                }
            ],
            "properties": {
                "Title": {
                    "title": {}
                },
                "Decision ID": {
                    "rich_text": {}
                },
                "Timestamp": {
                    "date": {}
                },
                "Outcome": {
                    "select": {
                        "options": [
                            {"name": "Success", "color": "green"},
                            {"name": "Failed", "color": "red"},
                            {"name": "Pending", "color": "yellow"},
                        ]
                    }
                },
                "Confidence": {
                    "number": {
                        "format": "percent"
                    }
                },
            }
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=10,
        )

        response.raise_for_status()
        data = response.json()
        return data.get("id")

    except requests.exceptions.RequestException as e:
        print(f"Failed to create Notion database: {e}")
        return None
