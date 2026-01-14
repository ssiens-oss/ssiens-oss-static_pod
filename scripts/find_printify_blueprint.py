#!/usr/bin/env python3
"""
Utility script to search Printify catalog for specific products
Usage: python scripts/find_printify_blueprint.py --search "gildan 18500"
"""
import os
import sys
import argparse
import requests
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

PRINTIFY_API = "https://api.printify.com/v1"


def get_api_key() -> Optional[str]:
    """Get Printify API key from environment"""
    api_key = os.getenv("PRINTIFY_API_KEY")
    if not api_key or api_key == "your-printify-api-key":
        print("❌ Error: PRINTIFY_API_KEY not set in .env file", file=sys.stderr)
        return None
    return api_key


def search_blueprints(api_key: str, search_term: str = "") -> List[Dict]:
    """
    Search Printify catalog for blueprints

    Args:
        api_key: Printify API key
        search_term: Optional search term to filter results

    Returns:
        List of matching blueprint dictionaries
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        print(f"🔍 Searching Printify catalog{f' for: {search_term}' if search_term else ''}...")
        response = requests.get(
            f"{PRINTIFY_API}/catalog/blueprints.json",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        blueprints = response.json()

        if search_term:
            search_lower = search_term.lower()
            blueprints = [
                bp for bp in blueprints
                if search_lower in bp.get("title", "").lower()
                or search_lower in bp.get("description", "").lower()
                or search_lower in bp.get("brand", "").lower()
            ]

        return blueprints

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching blueprints: {e}", file=sys.stderr)
        return []


def get_blueprint_providers(api_key: str, blueprint_id: int) -> List[Dict]:
    """
    Get available print providers for a blueprint

    Args:
        api_key: Printify API key
        blueprint_id: Blueprint ID

    Returns:
        List of provider dictionaries
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{PRINTIFY_API}/catalog/blueprints/{blueprint_id}/print_providers.json",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching providers for blueprint {blueprint_id}: {e}", file=sys.stderr)
        return []


def display_blueprint(blueprint: Dict, show_providers: bool = False, api_key: Optional[str] = None):
    """Display blueprint information in a formatted way"""
    print("\n" + "="*80)
    print(f"📦 {blueprint.get('title', 'Unknown')}")
    print("="*80)
    print(f"ID:          {blueprint.get('id')}")
    print(f"Brand:       {blueprint.get('brand', 'N/A')}")
    print(f"Model:       {blueprint.get('model', 'N/A')}")
    print(f"Description: {blueprint.get('description', 'N/A')}")

    if show_providers and api_key:
        providers = get_blueprint_providers(api_key, blueprint['id'])
        if providers:
            print(f"\n📍 Available Print Providers ({len(providers)}):")
            for provider in providers:
                print(f"   • ID {provider['id']:3d}: {provider['title']}")
                location = provider.get('location', {})
                if location:
                    print(f"      Location: {location.get('address1', '')}, {location.get('country', '')}")


def main():
    parser = argparse.ArgumentParser(
        description="Search Printify catalog for blueprints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for Gildan 18500 hoodie
  python scripts/find_printify_blueprint.py --search "gildan 18500"

  # Search for any hoodie
  python scripts/find_printify_blueprint.py --search "hoodie"

  # List all blueprints (can be long!)
  python scripts/find_printify_blueprint.py --all

  # Show specific blueprint with providers
  python scripts/find_printify_blueprint.py --id 165 --providers
        """
    )

    parser.add_argument(
        "--search", "-s",
        type=str,
        help="Search term to filter blueprints"
    )

    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="List all blueprints (can be very long)"
    )

    parser.add_argument(
        "--id", "-i",
        type=int,
        help="Show specific blueprint by ID"
    )

    parser.add_argument(
        "--providers", "-p",
        action="store_true",
        help="Show available print providers for each blueprint"
    )

    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=10,
        help="Limit number of results (default: 10)"
    )

    args = parser.parse_args()

    # Get API key
    api_key = get_api_key()
    if not api_key:
        sys.exit(1)

    # Handle specific blueprint ID
    if args.id:
        print(f"🔍 Fetching blueprint {args.id}...")
        providers = get_blueprint_providers(api_key, args.id)
        if providers:
            # Create a minimal blueprint dict for display
            blueprint = {"id": args.id, "title": f"Blueprint {args.id}"}
            display_blueprint(blueprint, show_providers=True, api_key=api_key)
        else:
            print(f"❌ Blueprint {args.id} not found or has no providers")
        sys.exit(0)

    # Search blueprints
    search_term = args.search if args.search else ("" if args.all else "gildan 18500")
    blueprints = search_blueprints(api_key, search_term)

    if not blueprints:
        print(f"❌ No blueprints found{f' matching: {search_term}' if search_term else ''}")
        sys.exit(1)

    print(f"✅ Found {len(blueprints)} blueprint(s)")

    # Limit results
    if len(blueprints) > args.limit and not args.all:
        print(f"📋 Showing first {args.limit} results (use --limit to see more)")
        blueprints = blueprints[:args.limit]

    # Display results
    for blueprint in blueprints:
        display_blueprint(blueprint, show_providers=args.providers, api_key=api_key)

    print("\n" + "="*80)
    print("💡 Tip: Use --providers flag to see available print providers")
    print("="*80)


if __name__ == "__main__":
    main()
