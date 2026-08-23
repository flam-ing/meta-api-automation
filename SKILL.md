---
name: 인스타 댓글 자동답
description: Instagram 댓글 자동답+DM을 공식 Meta 웹훅과 Cloudflare Worker로 만들 때 쓴다. 폴링 금지. Codex/Claude Code는 브라우저 조작이 꺼져 있으면 먼저 켠다. 이 파일을 드래그앤드롭해서 쓴다.
---
# 인스타 댓글 자동답 (웹훅 + Cloudflare)

이 파일을 받아서 **Codex** 또는 **Claude Code**에 드래그앤드롭 하면 된다.

릴리스: https://github.com/flam-ing/meta-api-automation/releases/latest
스킬 파일: https://github.com/flam-ing/meta-api-automation/releases/latest/download/SKILL.md

세션 쿠키 폴링, GitHub Actions 댓글 훑기, 30초/5분 루프는 쓰지 않는다. 계정 제한 난다.

## 이 스킬을 연 에이전트에게

1. **브라우저 조작이 필수다.** Meta 앱, Instagram Tester, Cloudflare 로그인은 브라우저가 있어야 한다.
   - Claude Code: Chrome / computer-use / 브라우저 MCP가 꺼져 있으면 먼저 켠다. 안 켜져 있으면 사용자에게 켜게 한 다음 진행한다.
   - Codex: browser 도구가 꺼져 있으면 설정에서 켠 뒤 진행한다.
   - 비밀번호, 2FA, 캡차는 사용자가 브라우저에서 직접 한다. 에이전트는 그 세션으로 나머지를 한다.
2. **공식 Meta 웹훅만** 쓴다. 댓글 목록을 주기적으로 조회하지 않는다.
3. 호스트는 **Cloudflare Worker** (무료 `*.workers.dev`면 충분). 도메인을 사지 않아도 된다. `github.io`는 웹훅으로 쓰지 않는다.
4. 연결은 **Instagram Login 유저 토큰** (`IGAA…`) 이다. Facebook Page 토큰은 필수가 아니다.
5. 시크릿을 채팅/깃/프론트에 붙이지 않는다.

## 기본 문구

- 공개 답글: `DM 드렸습니다!`
- DM:
  - `방법을 알고 싶으면 https://ai-ing.org 를 확인해 주세요.`
  - `같은 자동답을 쓰려면 스킬을 받아 Codex나 Claude Code에 드래그앤드롭 하세요: https://github.com/flam-ing/meta-api-automation/releases/latest/download/SKILL.md`
  - `브라우저 조작이 꺼져 있으면 먼저 켜세요.`
- 자기 계정 댓글은 건너뛴다.

## 만드는 순서

1. 브라우저가 켜져 있는지 확인한다. 꺼져 있으면 켠다.
2. Instagram을 Professional (Business 또는 Creator) 로 둔다.
3. developers.facebook.com 에서 앱을 만들고 Instagram Login 권한을 넣는다: instagram_business_basic, instagram_business_manage_comments, instagram_business_manage_messages
4. 개발 모드면 해당 IG를 Instagram Tester로 추가하고 초대를 수락한다.
5. Instagram Login으로 유저 토큰을 받는다. IGAA로 시작하는 ASCII. 마스킹 점 복사 금지.
6. Cloudflare 계정 (Google 로그인으로 충분). wrangler login을 브라우저에서 승인한다.
7. Worker를 배포한다. GET 핸드셰이크, POST 서명 검증, 댓글 답글+DM. 자기 댓글 skip. 같은 comment id 두 번 답 금지.
8. Worker 시크릿: WEBHOOK_VERIFY_TOKEN, META_APP_SECRET, IG_USER_ACCESS_TOKEN, IG_GRAPH_USER_ID
9. Meta 앱 웹훅 콜백을 Worker URL로 넣고 comments 구독.
10. POST /me/subscribed_apps?subscribed_fields=comments
11. 다른 계정으로 테스트 댓글. 폴링으로 확인하지 않는다.

## 하지 말 것

- 세션/쿠키로 댓글 폴링
- GitHub Actions나 cron으로 댓글 목록 조회
- 토큰을 PR/채팅에 붙이기
- github.io를 웹훅 URL로 쓰기

## 막히면

- Insufficient Developer Role → Instagram Tester 추가 후 초대 수락
- 토큰이 IGAA + 점 → 마스킹 복사
- 콜백이 홈 HTML → Worker 미배포. wrangler는 프로젝트 루트에서 deploy
- 브라우저 도구 없음 → Codex/Claude Code에서 브라우저를 켠 다음 진행
- 앱 unpublished면 테스터 외 댓글은 웹훅이 안 올 수 있다
