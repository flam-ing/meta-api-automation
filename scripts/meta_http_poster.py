#!/usr/bin/env python3
"""
Pure HTTP REST API Instagram Publisher v2 (ZERO BROWSER, Pure Requests).
Uploads JPEG binary with proper X-Instagram-Rupload-Params and configures post.
"""

import os
import json
import time
import requests
from PIL import Image

PNG_PATH = "/Users/minwokim/Documents/Codex/meta_automation/test_white_post.png"
JPG_PATH = "/Users/minwokim/Documents/Codex/meta_automation/test_white_post.jpg"
COOKIES_FILE = "/Users/minwokim/Documents/Codex/meta_automation/meta_session_tokens.json"
CAPTION = "이 게시글은 AI로 올린 테스트 글입니다."

def ensure_jpeg():
    # Convert PNG to clean standard RGB JPEG
    im = Image.open(PNG_PATH).convert("RGB")
    im.save(JPG_PATH, "JPEG", quality=95)
    print(f"✅ Converted PNG to JPEG: {JPG_PATH} ({os.path.getsize(JPG_PATH)} bytes)")

def publish_pure_http():
    ensure_jpeg()

    with open(COOKIES_FILE, "r") as f:
        data = json.load(f)

    ig_cookies = data.get("instagram_cookies", {})
    csrf_token = ig_cookies.get("csrftoken")
    ds_user_id = ig_cookies.get("ds_user_id")

    with open(JPG_PATH, "rb") as f:
        jpg_bytes = f.read()

    upload_id = str(int(time.time() * 1000))
    photo_name = f"fb_uploader_{upload_id}"

    session = requests.Session()
    session.cookies.update(ig_cookies)

    rupload_params = json.dumps({
        "upload_id": upload_id,
        "media_type": 1,
        "client_passthrough_id": upload_id
    })

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "X-CSRFToken": csrf_token,
        "X-IG-App-ID": "936619743392459",
        "X-Instagram-AJAX": "1019623829",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.instagram.com",
        "Referer": "https://www.instagram.com/",
        "Accept": "*/*"
    }

    print("============================================================")
    print("🚀 PURE HTTP INSTAGRAM REST API POSTING (ZERO BROWSER)")
    print("============================================================")
    print(f"📸 Image: {JPG_PATH} ({len(jpg_bytes)} bytes)")
    print(f"✍️ Caption: '{CAPTION}'")
    print(f"🆔 Upload ID: {upload_id}")

    # Step 1: Upload Raw JPEG
    upload_url = f"https://www.instagram.com/rupload_igphoto/{photo_name}"
    upload_headers = headers.copy()
    upload_headers.update({
        "X-Entity-Name": photo_name,
        "X-Entity-Length": str(len(jpg_bytes)),
        "X-Entity-Type": "image/jpeg",
        "Offset": "0",
        "X-Instagram-Rupload-Params": rupload_params,
        "Content-Type": "image/jpeg"
    })

    print("\n[HTTP Step 1] Uploading binary JPEG data...")
    upload_res = session.post(upload_url, data=jpg_bytes, headers=upload_headers, timeout=30)
    print(f"Status Code: {upload_res.status_code}")
    print("Upload Response:\n", upload_res.text)

    # Step 2: Configure / Publish
    config_url = "https://www.instagram.com/api/v1/media/configure/"
    config_data = {
        "upload_id": upload_id,
        "caption": CAPTION,
        "source_type": "4",
        "disable_comments": "0",
        "like_and_view_counts_disabled": "0",
        "client_shared_at": str(int(time.time()))
    }

    config_headers = headers.copy()
    config_headers["Content-Type"] = "application/x-www-form-urlencoded"

    print("\n[HTTP Step 2] Calling /api/v1/media/configure/ endpoint...")
    config_res = session.post(config_url, data=config_data, headers=config_headers, timeout=30)
    print(f"Status Code: {config_res.status_code}")
    print("Publish Response:\n", config_res.text)

    try:
        res_json = config_res.json()
        if res_json.get("status") == "ok":
            media = res_json.get("media", {})
            media_id = media.get("id")
            code = media.get("code")
            post_url = f"https://www.instagram.com/p/{code}/" if code else "N/A"
            print("\n🎉 SUCCESS! Post Published 100% via Pure HTTP REST API (Zero Browser)!")
            print(f"🔗 Post URL: {post_url}")
            print(f"🆔 Media ID: {media_id}")
            return {"success": True, "post_url": post_url, "media_id": media_id}
        else:
            return {"success": False, "response": res_json}
    except Exception as e:
        print("❌ Error:", e)
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    publish_pure_http()
