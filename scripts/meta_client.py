#!/usr/bin/env python3
"""
Universal Meta Graph API HTTP Client.
Pure HTTP REST client supporting Instagram, Facebook, and Threads without browser dependencies.
"""

import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

class MetaAPIClient:
    def __init__(self, app_id=None, app_secret=None, access_token=None, api_version=None):
        self.app_id = app_id or os.getenv("META_APP_ID")
        self.app_secret = app_secret or os.getenv("META_APP_SECRET")
        self.api_version = api_version or os.getenv("META_GRAPH_API_VERSION", "v20.0")
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
        # Access Token fallback: Explicit Token -> Env Token -> App Access Token (app_id|app_secret)
        self.access_token = (
            access_token or
            os.getenv("META_APP_ACCESS_TOKEN") or
            os.getenv("META_USER_ACCESS_TOKEN") or
            (f"{self.app_id}|{self.app_secret}" if self.app_id and self.app_secret else None)
        )

    def _request(self, method, endpoint, params=None, data=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        params = params or {}
        if self.access_token and "access_token" not in params:
            params["access_token"] = self.access_token

        try:
            res = requests.request(method, url, params=params, json=data, timeout=15)
            try:
                return res.json()
            except Exception:
                return {"status_code": res.status_code, "text": res.text}
        except Exception as e:
            return {"error": str(e)}

    def get_app_info(self):
        """Fetches registered Meta application details."""
        if not self.app_id:
            return {"error": "META_APP_ID is not configured"}
        return self._request("GET", f"/{self.app_id}", params={"fields": "id,name,link,category"})

    def debug_token(self, token_to_inspect=None):
        """Inspects token validity and scopes via debug_token endpoint."""
        token = token_to_inspect or self.access_token
        if not token:
            return {"error": "No token provided to inspect"}
        return self._request("GET", "/debug_token", params={"input_token": token})

    def get_profile(self, user_id="me", fields="id,name,email"):
        """Fetches user or page profile information."""
        return self._request("GET", f"/{user_id}", params={"fields": fields})

    def publish_facebook_page_post(self, page_id, message, link=None):
        """Publishes a text or link post to a Facebook Page."""
        payload = {"message": message}
        if link:
            payload["link"] = link
        return self._request("POST", f"/{page_id}/feed", data=payload)

    def publish_instagram_photo(self, ig_user_id, image_url, caption=""):
        """Publishes an image post to an Instagram Professional/Business account."""
        # Step 1: Create media container
        container_res = self._request("POST", f"/{ig_user_id}/media", data={
            "image_url": image_url,
            "caption": caption
        })
        
        container_id = container_res.get("id")
        if not container_id:
            return {"error": "Failed to create media container", "details": container_res}

        # Step 2: Publish media container
        publish_res = self._request("POST", f"/{ig_user_id}/media_publish", data={
            "creation_id": container_id
        })
        return publish_res

def main():
    parser = argparse.ArgumentParser(description="Universal Meta Graph API Client")
    parser.add_argument("--action", choices=["status", "get-profile", "post-fb", "post-ig"], default="status")
    parser.add_argument("--page-id", type=str, help="Facebook Page ID")
    parser.add_argument("--ig-user-id", type=str, help="Instagram Business User ID")
    parser.add_argument("--message", type=str, help="Message/Post text")
    parser.add_argument("--image-url", type=str, help="Public Image URL for Instagram")
    parser.add_argument("--caption", type=str, default="", help="Caption for Instagram Post")
    args = parser.parse_args()

    client = MetaAPIClient()

    if args.action == "status":
        print("🔍 Checking Meta Graph API Status...")
        app_res = client.get_app_info()
        print("📱 App Info:", json.dumps(app_res, indent=2, ensure_ascii=False))
        debug_res = client.debug_token()
        print("🔑 Token Debug:", json.dumps(debug_res, indent=2, ensure_ascii=False))
    elif args.action == "get-profile":
        profile = client.get_profile()
        print("👤 Profile:", json.dumps(profile, indent=2, ensure_ascii=False))
    elif args.action == "post-fb":
        if not args.page_id or not args.message:
            print("Error: --page-id and --message required", file=sys.stderr)
            sys.exit(1)
        res = client.publish_facebook_page_post(args.page_id, args.message)
        print("📘 Facebook Post Result:", json.dumps(res, indent=2, ensure_ascii=False))
    elif args.action == "post-ig":
        if not args.ig_user_id or not args.image_url:
            print("Error: --ig-user-id and --image-url required", file=sys.stderr)
            sys.exit(1)
        res = client.publish_instagram_photo(args.ig_user_id, args.image_url, args.caption)
        print("📸 Instagram Post Result:", json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
