"""
AliExpress OAuth 2.0 Authentication Helper
Complete implementation for getting and managing access tokens
"""
import requests
import hmac
import hashlib
import time
import json
from typing import Dict, Optional
from loguru import logger


class AliExpressAuth:
    """Helper class for AliExpress OAuth authentication"""

    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = "https://api-sg.aliexpress.com/rest"
        self.oauth_url = "https://oauth.aliexpress.com"

    def get_authorization_url(
        self,
        redirect_uri: str,
        state: Optional[str] = None,
        force_auth: bool = False,
    ) -> str:
        """
        Generate authorization URL for OAuth flow

        Args:
            redirect_uri: Your callback URL
            state: Optional CSRF token
            force_auth: Force re-authentication

        Returns:
            Authorization URL to redirect user to
        """
        params = {
            "response_type": "code",
            "client_id": self.app_key,
            "redirect_uri": redirect_uri,
            "state": state or "random_state_123",
            "view": "web",  # or 'wap' for mobile
            "sp": "ae",  # AliExpress
        }

        if force_auth:
            params["force_auth"] = "true"

        # Build query string
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"{self.oauth_url}/authorize?{query_string}"

        logger.info(f"Authorization URL generated: {auth_url}")
        return auth_url

    def _generate_signature(self, endpoint: str, params: Dict[str, str]) -> str:
        """
        Generate HMAC-SHA256 signature for API requests

        Args:
            endpoint: API endpoint path
            params: Request parameters

        Returns:
            Signature string
        """
        # Sort parameters alphabetically
        sorted_keys = sorted(params.keys())

        # Concatenate: endpoint + key1 + value1 + key2 + value2 ...
        concatenated = endpoint + "".join([f"{key}{params[key]}" for key in sorted_keys])

        # Generate HMAC-SHA256 signature
        sign = hmac.new(
            self.app_secret.encode("utf-8"),
            concatenated.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest().upper()

        return sign

    def exchange_code_for_token(self, code: str) -> Dict[str, any]:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from callback

        Returns:
            Token data including access_token and refresh_token
        """
        endpoint = "/auth/token/create"
        timestamp = str(int(time.time() * 1000))

        params = {
            "app_key": self.app_key,
            "timestamp": timestamp,
            "sign_method": "sha256",
            "code": code,
        }

        # Generate and add signature
        params["sign"] = self._generate_signature(endpoint, params)

        # Make request
        url = self.base_url + endpoint
        logger.info(f"Exchanging code for token: {url}")

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check for errors
            if data.get("code") != "0":
                error_msg = data.get("message", "Unknown error")
                raise Exception(f"Token exchange failed: {error_msg}")

            result = data.get("resp_result", {}).get("result", {})

            logger.info("✅ Successfully obtained access token")

            return {
                "access_token": result.get("access_token"),
                "refresh_token": result.get("refresh_token"),
                "expires_in": result.get("expires_in"),  # Seconds
                "refresh_expires_in": result.get("refresh_expires_in"),
                "user_id": result.get("user_id"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to exchange code: {e}")
            raise

    def refresh_access_token(self, refresh_token: str) -> Dict[str, any]:
        """
        Refresh expired access token

        Args:
            refresh_token: Refresh token from previous authentication

        Returns:
            New token data
        """
        endpoint = "/auth/token/refresh"
        timestamp = str(int(time.time() * 1000))

        params = {
            "app_key": self.app_key,
            "timestamp": timestamp,
            "sign_method": "sha256",
            "refresh_token": refresh_token,
        }

        params["sign"] = self._generate_signature(endpoint, params)

        url = self.base_url + endpoint
        logger.info("Refreshing access token...")

        try:
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get("code") != "0":
                error_msg = data.get("message", "Unknown error")
                raise Exception(f"Token refresh failed: {error_msg}")

            result = data.get("resp_result", {}).get("result", {})

            logger.info("✅ Successfully refreshed access token")

            return {
                "access_token": result.get("access_token"),
                "refresh_token": result.get("refresh_token"),
                "expires_in": result.get("expires_in"),
                "refresh_expires_in": result.get("refresh_expires_in"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh token: {e}")
            raise

    def save_tokens_to_file(self, tokens: Dict[str, any], filename: str = ".aliexpress_tokens.json"):
        """
        Save tokens to file for persistence

        Args:
            tokens: Token data
            filename: File to save to
        """
        with open(filename, "w") as f:
            json.dump(tokens, f, indent=2)

        logger.info(f"Tokens saved to {filename}")

    def load_tokens_from_file(self, filename: str = ".aliexpress_tokens.json") -> Optional[Dict[str, any]]:
        """
        Load tokens from file

        Args:
            filename: File to load from

        Returns:
            Token data or None if file doesn't exist
        """
        try:
            with open(filename, "r") as f:
                tokens = json.load(f)

            logger.info(f"Tokens loaded from {filename}")
            return tokens

        except FileNotFoundError:
            logger.warning(f"Token file {filename} not found")
            return None


# CLI tool for authentication
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    app_key = os.getenv("ALIEXPRESS_APP_KEY")
    app_secret = os.getenv("ALIEXPRESS_APP_SECRET")

    if not app_key or not app_secret:
        print("❌ Please set ALIEXPRESS_APP_KEY and ALIEXPRESS_APP_SECRET in .env")
        exit(1)

    auth = AliExpressAuth(app_key, app_secret)

    print("\n" + "=" * 60)
    print("AliExpress OAuth Authentication Tool")
    print("=" * 60 + "\n")

    # Step 1: Generate authorization URL
    redirect_uri = input("Enter your redirect URI (e.g., https://yourapp.com/callback): ").strip()

    if not redirect_uri:
        redirect_uri = "http://localhost:8000/callback"
        print(f"Using default: {redirect_uri}")

    auth_url = auth.get_authorization_url(redirect_uri)

    print("\n📋 STEP 1: Get Authorization Code")
    print("-" * 60)
    print(f"\n1. Open this URL in your browser:\n\n{auth_url}\n")
    print("2. Login and authorize the app")
    print("3. Copy the 'code' parameter from the redirect URL\n")

    code = input("Enter the authorization code: ").strip()

    if not code:
        print("❌ No code provided. Exiting.")
        exit(1)

    # Step 2: Exchange code for tokens
    print("\n🔄 STEP 2: Exchanging code for tokens...")
    print("-" * 60)

    try:
        tokens = auth.exchange_code_for_token(code)

        print("\n✅ SUCCESS! Tokens obtained:\n")
        print(f"Access Token: {tokens['access_token'][:20]}...")
        print(f"Refresh Token: {tokens['refresh_token'][:20]}...")
        print(f"Expires in: {tokens['expires_in']} seconds ({tokens['expires_in']/3600:.1f} hours)")
        print(f"User ID: {tokens['user_id']}")

        # Save to file
        auth.save_tokens_to_file(tokens)

        # Update .env file
        print("\n📝 Add these to your .env file:\n")
        print(f"ALIEXPRESS_ACCESS_TOKEN={tokens['access_token']}")
        print(f"ALIEXPRESS_REFRESH_TOKEN={tokens['refresh_token']}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)

    print("\n" + "=" * 60)
    print("Authentication complete! You can now use the API.")
    print("=" * 60 + "\n")
