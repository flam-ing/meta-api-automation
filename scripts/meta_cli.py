#!/usr/bin/env python3
"""
Universal Meta CLI Interface.
Supports status checking, Instagram & Facebook headless publishing and feed reading.
"""

import os
import sys
import json
import asyncio
import argparse
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

CDP_PORT = int(os.getenv("META_CDP_PORT", "9222"))
CDP_URL = f"http://localhost:{CDP_PORT}"

class MetaAutomationSuite:
    def __init__(self, cdp_url=CDP_URL):
        self.cdp_url = cdp_url

    async def get_browser(self, p):
        try:
            return await p.chromium.connect_over_cdp(self.cdp_url)
        except Exception as e:
            print(f"❌ Error connecting to Chrome CDP at {self.cdp_url}: {e}", file=sys.stderr)
            print("💡 Hint: Ensure Chrome is launched with --remote-debugging-port=9222", file=sys.stderr)
            return None

    async def check_status(self):
        async with async_playwright() as p:
            browser = await self.get_browser(p)
            if not browser:
                return {"cdp_connected": False}

            context = browser.contexts[0]
            page = await context.new_page()
            
            # Check Instagram
            await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            ig_logged = "login" not in page.url and (await page.query_selector("nav, svg[aria-label='홈']")) is not None

            # Check Facebook
            await page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            fb_logged = "login" not in page.url and (await page.query_selector("div[role='navigation'], input[placeholder*='무슨 생각']")) is not None

            await page.close()
            return {
                "cdp_connected": True,
                "instagram_logged_in": ig_logged,
                "facebook_logged_in": fb_logged
            }

    async def read_feed(self, platform="instagram", limit=5):
        async with async_playwright() as p:
            browser = await self.get_browser(p)
            if not browser:
                return []

            context = browser.contexts[0]
            page = await context.new_page()

            posts = []
            if platform == "instagram":
                await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                articles = await page.query_selector_all("article")
                for art in articles[:limit]:
                    txt = await art.inner_text()
                    lines = [l.strip() for l in txt.split("\n") if l.strip()]
                    posts.append(lines[:4])
            elif platform == "facebook":
                await page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                feed_items = await page.query_selector_all("div[role='feed'] > div, div[role='article']")
                for fi in feed_items[:limit]:
                    txt = await fi.inner_text()
                    lines = [l.strip() for l in txt.split("\n") if l.strip()]
                    if lines:
                        posts.append(lines[:3])

            await page.close()
            return posts

    async def post_instagram(self, image_path, caption=""):
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}", file=sys.stderr)
            return False

        async with async_playwright() as p:
            browser = await self.get_browser(p)
            if not browser:
                return False

            context = browser.contexts[0]
            page = await context.new_page()
            await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            # Click create button
            create_btn = await page.query_selector("svg[aria-label='만들기'], svg[aria-label='새로운 게시물'], text=만들기")
            if create_btn:
                await create_btn.click()
                await page.wait_for_timeout(2000)

            # Set file input
            file_input = await page.query_selector("input[type='file']")
            if file_input:
                await file_input.set_input_files(os.path.abspath(image_path))
                await page.wait_for_timeout(3000)

                # Click next until caption screen
                for _ in range(2):
                    next_btn = await page.query_selector("div[role='button']:has-text('다음'), button:has-text('다음')")
                    if next_btn:
                        await next_btn.click()
                        await page.wait_for_timeout(2000)

                # Type caption
                if caption:
                    cap_box = await page.query_selector("div[aria-label*='문구 입력'], div[contenteditable='true']")
                    if cap_box:
                        await cap_box.fill(caption)
                        await page.wait_for_timeout(1000)

                # Click share
                share_btn = await page.query_selector("div[role='button']:has-text('공유하기'), button:has-text('공유하기')")
                if share_btn:
                    await share_btn.click()
                    await page.wait_for_timeout(5000)
                    print("🎉 Instagram Post successfully shared!")
                    await page.close()
                    return True

            await page.close()
            return False

    async def post_facebook(self, text):
        async with async_playwright() as p:
            browser = await self.get_browser(p)
            if not browser:
                return False

            context = browser.contexts[0]
            page = await context.new_page()
            await page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            # Click create post trigger
            trigger = await page.query_selector("span:has-text('무슨 생각을 하고 계신가요?'), div[role='button']:has-text('무슨 생각')")
            if trigger:
                await trigger.click()
                await page.wait_for_timeout(2000)

                # Type text into modal
                text_box = await page.query_selector("div[role='textbox'], div[contenteditable='true']")
                if text_box:
                    await text_box.fill(text)
                    await page.wait_for_timeout(1000)

                    # Click post
                    post_btn = await page.query_selector("div[aria-label='게시'], div[role='button']:has-text('게시')")
                    if post_btn:
                        await post_btn.click()
                        await page.wait_for_timeout(4000)
                        print("🎉 Facebook Post successfully published!")
                        await page.close()
                        return True

            await page.close()
            return False

def main():
    parser = argparse.ArgumentParser(description="Universal Meta CLI Suite")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Status
    subparsers.add_parser("status", help="Check session login status")

    # Read feeds
    ig_read = subparsers.add_parser("read-ig", help="Read Instagram home feed")
    ig_read.add_argument("--limit", type=int, default=5)

    fb_read = subparsers.add_parser("read-fb", help="Read Facebook home feed")
    fb_read.add_argument("--limit", type=int, default=5)

    # Post
    ig_post = subparsers.add_parser("post-ig", help="Publish Instagram photo post")
    ig_post.add_argument("--image", type=str, required=True, help="Path to image")
    ig_post.add_argument("--caption", type=str, default="", help="Caption with hashtags")

    fb_post = subparsers.add_parser("post-fb", help="Publish Facebook text post")
    fb_post.add_argument("--text", type=str, required=True, help="Post text content")

    args = parser.parse_args()
    suite = MetaAutomationSuite()

    if args.command == "status":
        res = asyncio.run(suite.check_status())
        print("📊 Meta Session Status:", json.dumps(res, indent=2))
    elif args.command == "read-ig":
        posts = asyncio.run(suite.read_feed("instagram", args.limit))
        print(f"📸 Instagram Feed ({len(posts)} items):", json.dumps(posts, indent=2, ensure_ascii=False))
    elif args.command == "read-fb":
        posts = asyncio.run(suite.read_feed("facebook", args.limit))
        print(f"📘 Facebook Feed ({len(posts)} items):", json.dumps(posts, indent=2, ensure_ascii=False))
    elif args.command == "post-ig":
        asyncio.run(suite.post_instagram(args.image, args.caption))
    elif args.command == "post-fb":
        asyncio.run(suite.post_facebook(args.text))

if __name__ == "__main__":
    main()
