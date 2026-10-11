---
name: 인스타 댓글 자동답
description: Instagram 댓글 자동답+DM을 공식 Meta 웹훅과 Cloudflare Worker로 만들 때 쓴다. 폴링 금지. Codex/Claude Code는 브라우저 조작이 꺼져 있으면 먼저 켠다.
---
# 인스타 댓글 자동답 (웹훅 + Cloudflare)

이 파일을 받아서 Codex 또는 Claude Code에 드래그앤드롭 하면 된다. 세션 쿠키 폴링, GitHub Actions 댓글 훑기, 30초/5분 루프는 쓰지 않는다.

## 이 스킬을 연 에이전트에게
1. 브라우저 조작이 필수다. Meta/Cloudflare 로그인에 필요하다.
   - Claude Code: Chrome/computer-use/브라우저 MCP가 꺼져 있으면 먼저 켠다.
   - Codex: browser 도구가 꺼져 있으면 설정에서 켠다.
   - 비밀번호/2FA/캡차는 사용자가 한다.
2. 공식 Meta 웹훅만 쓴다. 댓글을 주기적으로 조회하지 않는다.
3. 호스트는 Cloudflare Worker (*.workers.dev이면 충분). github.io 금지.
4. Instagram Login 유저 토큰(IGAA)을 Worker 시크릿으로 넣는다. Page 토큰 불필요.
5. 시크릿을 채팅/깃에 붙이지 않는다.

## 기본 문구
- 공개 답글: DM 드렸습니다!
- DM: https://ai-ing.org 그리고 이 스킬 https://ig-comment-webhook.rlaalsdn4564.workers.dev/skill.md
- 브라우저 조작이 꺼져 있으면 먼저 켜세요.
- 자기 댓글 skip

## 순서
1. 브라우저 켜기
2. IG Professional
3. Meta 앱 + Instagram Login 권한(basic, manage_comments, manage_messages)
4. Tester 초대 수락
5. 유저 토큰(IGAA ASCII, 마스킹 점 금지)
6. wrangler login 후 Worker deploy
7. GET 핸드셰이크 / POST 서명 검증 / 답글+DM
8. 시크릿: WEBHOOK_VERIFY_TOKEN, META_APP_SECRET, IG_USER_ACCESS_TOKEN, IG_GRAPH_USER_ID
9. 콜백을 Worker URL로, comments 구독, POST /me/subscribed_apps
10. 다른 계정으로 테스트. 폴링 금지.
