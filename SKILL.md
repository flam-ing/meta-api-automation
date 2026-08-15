---
name: meta-api-automation
description: >-
  Universal Meta (Instagram, Facebook, Threads) API and Headless Automation Skill.
  Allows agents to publish posts/reels, read feeds/comments, extract Graph API tokens,
  and automate social interactions via pure HTTP REST API or session-based automation.
---

# Meta (Instagram & Facebook) API & Automation Skill

This skill enables AI agents to interact with Meta platforms (Instagram, Facebook Graph API, Threads) either via **official REST API endpoints** (pure HTTP, zero-browser) or **headless session automation** (Playwright CDP).

## 🌟 Supported Capabilities
1. **Instagram & Facebook Post Publishing**:
   - Single image & carousel post publishing
   - Video / Reels upload and scheduling
   - Text status updates with link previews
2. **Social Feed & Comment Reading**:
   - Fetching user timeline, page feed, or public hashtags
   - Reading post comments and engagement metrics
3. **Automated Engagement & Responses**:
   - Automated comment replies
   - Direct Message (DM) query response workflows
4. **Universal Multi-User Credentials & Token Extraction**:
   - Graph API token validation & inspection (`debug_token`)
   - Server-to-server App Access Token (`{app_id}|{app_secret}`)
   - Automated token extraction helper via Chrome CDP

---

## 🛠️ Prerequisites & Configuration

Credentials can be provided via environment variables in `~/.env`, `.env` in the current workspace, or passed as CLI arguments:

```env
# Meta Official API Credentials (Optional if using Headless mode)
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_APP_ACCESS_TOKEN=your_app_id|your_app_secret
META_USER_ACCESS_TOKEN=your_user_token_if_available
META_PAGE_ACCESS_TOKEN=your_page_token_if_available

# Target User / Page IDs
META_IG_USER_ID=your_instagram_user_id
META_FB_USER_ID=your_facebook_user_id
META_FB_PAGE_ID=your_facebook_page_id
```

---

## 🚀 Script Inventory & Entry Points

All scripts are located in `/Users/minwokim/.gemini/config/skills/meta-api-automation/scripts/`:

### 1. Pure HTTP REST API Client (`meta_client.py`)
```bash
# Check App & Token Status
python3 meta_client.py --action status

# Read user profile / page metadata
python3 meta_client.py --action get-profile

# Publish post to Facebook Page
python3 meta_client.py --action post-fb --page-id "PAGE_ID" --message "Hello from AI Agent"

# Publish image post to Instagram Business Account
python3 meta_client.py --action post-ig --ig-user-id "IG_USER_ID" --image-url "https://example.com/img.jpg" --caption "My Caption #AI"
```

### 2. Unified CLI Interface (`meta_cli.py`)
```bash
# Status check across all configured channels
python3 meta_cli.py status

# Post to Instagram (Headless Session Mode)
python3 meta_cli.py post-ig --image /path/to/image.png --caption "AI Generated Post #Automation"

# Post to Facebook Feed
python3 meta_cli.py post-fb --text "Weekly update from AI Agent!"

# Read Instagram Home Feed
python3 meta_cli.py read-ig --limit 5
```

### 3. Headless Browser Launcher & Session Tool (`meta_session_helper.py`)
Used when Graph API permissions are in development mode or user needs session-based scraping:
```bash
python3 meta_session_helper.py --port 9222 --profile-dir ~/.meta_chrome_profile
```

---

## 🤖 Agent Interaction Guidelines
- For routing, troubleshooting, and architectural details, refer to [`AGENTS.md`](file:///Users/minwokim/.gemini/config/skills/meta-api-automation/AGENTS.md).
- Prioritize **Pure HTTP API (`meta_client.py`)** when `META_APP_ACCESS_TOKEN` or `META_PAGE_ACCESS_TOKEN` is present.
- Fall back to **Headless Session Mode (`meta_cli.py`)** if the app is still in development mode without required OAuth review scopes.
