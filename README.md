# 🌐 Meta (Instagram, Facebook, Threads) API & Automation Suite

범용적인 **Meta(인스타그램 / 페이스북 / 스레드) 공식 Graph API 연동 및 브라우저 세션 무인 자동화 엔진**입니다.

이 도구는 **어떤 사용자나 개발자든** 자신의 Meta App Key 또는 브라우저 로그인 세션만 연결하면, 인스타그램 포스팅, 릴스 업로드, 페이스북 글 게시, 피드 읽기, 댓글 및 DM 자동 응답을 100% 무인으로 수행할 수 있도록 설계되었습니다.

---

## 🌟 주요 기능 (Capabilities)

### 1. 📸 인스타그램(Instagram) 자동화
* **피드 & 카드뉴스 포스팅**: 이미지 파일과 본문, 해시태그를 전달하여 즉시 업로드
* **릴스 (Reels) 동영상 업로드**: 숏폼/영상 자동 게시 및 캡션 작성
* **홈 피드 및 인기 게시물 수집**: 실시간 타임라인, 특정 해시태그 게시물 스크래핑 및 트렌드 분석
* **댓글 및 DM 모니터링**: 고객 문의 댓글/DM 실시간 감지 및 AI 자동 답장

### 2. 📘 페이스북(Facebook) 자동화
* **개인 프로필 & 페이지 글 자동 발행**: 텍스트, 이미지, 링크 미리보기 자동 게시
* **타임라인 및 피드 읽기**: 내 피드 및 팔로우 페이지 최신 소식 수집
* **페이지 통계 및 인사이트 조회**: 조회수, 인터랙션 데이터 Graph API 조회

### 3. 🧵 스레드(Threads) 연동
* **텍스트 & 미디어 자동 포스팅**: 개발자 App ID(`THREADS_APP_ID`)를 활용한 스레드 자동 글 배포

### 4. ⚡ 듀얼 엔진 구조 (Dual-Engine Architecture)
1. **Engine 1: Pure HTTP REST API (`meta_client.py`)**
   * 브라우저 없이 서버/클라우드/서버리스 환경(Vercel, Lambda, VPS)에서 cURL 및 Python `requests`로 100ms 내 초고속 동작
   * 영구 서버 토큰(`{app_id}|{app_secret}`) 지원
2. **Engine 2: Headless Browser CDP Session (`meta_cli.py`)**
   * Meta의 까다로운 앱 검수(App Review)나 권한 승인 절차 없이도, 브라우저 세션을 통해 개인 계정의 모든 기능을 즉시 자동화

---

## 🚀 빠른 시작 (Quick Start)

### 1. 환경 설정
프로젝트 루트 또는 `~/.env`에 본인의 Meta 정보를 설정합니다. (`.env.example` 복사)

```bash
cp .env.example .env
```

```env
# Meta 공식 앱 기본 정보
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_APP_ACCESS_TOKEN=your_app_id|your_app_secret
META_GRAPH_API_VERSION=v20.0
META_GRAPH_API_URL=https://graph.facebook.com/v20.0/

# 사용자 계정 메타데이터
META_FB_USER_ID=your_facebook_user_id
META_IG_USER_ID=your_instagram_user_id
```

### 2. 의존성 패키지 설치
```bash
pip install requests python-dotenv playwright
playwright install chromium
```

---

## 💻 CLI 명령어 사용법 (CLI Reference)

### 1. 상태 및 토큰 검증
```bash
# 공식 Graph API 연결 상태 및 토큰 유효성 확인
python3 scripts/meta_client.py --action status

# 전체 채널(인스타/페북/브라우저 세션) 상태 종합 진단
python3 scripts/meta_cli.py status
```

### 2. 인스타그램 포스팅 및 피드 읽기
```bash
# 인스타그램 사진 + 캡션 포스팅
python3 scripts/meta_cli.py post-ig --image /path/to/photo.jpg --caption "에이아잉 AI 자동화 테스트! #AI #Automation"

# 인스타그램 홈 피드 최신 5건 수집
python3 scripts/meta_cli.py read-ig --limit 5
```

### 3. 페이스북 글 작성 및 피드 읽기
```bash
# 페이스북 상태 메시지 작성
python3 scripts/meta_cli.py post-fb --text "오늘의 AI 비즈니스 인사이트 공유합니다."

# 페이스북 최신 피드 수집
python3 scripts/meta_cli.py read-fb --limit 5
```

---

## 📡 Python 코드로 직접 호출하기 (SDK Usage)

```python
from scripts.meta_client import MetaAPIClient

# 1. 클라이언트 초기화 (자동으로 .env 로드)
client = MetaAPIClient()

# 2. 공식 앱 정보 및 토큰 디버깅
app_info = client.get_app_info()
print("App Name:", app_info.get("name"))

# 3. 페이스북 페이지 포스팅 (HTTP REST API)
res = client.publish_facebook_page_post(
    page_id="YOUR_PAGE_ID",
    message="AI 에이전트가 발행한 자동 게시물입니다!"
)
print("Post ID:", res.get("id"))
```

---

## 🤖 AI 에이전트 연동 가이드
AI 에이전트가 이 모듈을 자율적으로 사용할 수 있도록 라우팅 규칙 및 상세 프로토콜이 [`AGENTS.md`](file:///Users/minwokim/.gemini/config/skills/meta-api-automation/AGENTS.md)에 정의되어 있습니다.
