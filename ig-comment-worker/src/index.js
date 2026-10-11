import DM_MAP_FILE from './dm-map.json';
/**
 * Instagram comments webhook (Cloudflare Worker)
 * Official Meta webhooks only. No polling.
 *
 * Secrets:
 *   WEBHOOK_VERIFY_TOKEN, META_APP_SECRET,
 *   IG_USER_ACCESS_TOKEN, IG_GRAPH_USER_ID
 */
const GRAPH = 'https://graph.instagram.com/v25.0';
const COMMENT_REPLY = 'DM 드렸습니다!';
const DM_TEXT = '방법을 알고 싶으면 https://ai-ing.org 를 확인해 주세요. 같은 자동답을 쓰려면 스킬을 받아 Codex나 Claude Code에 드래그앤드롭 하세요: https://github.com/flam-ing/meta-api-automation/releases/latest/download/SKILL.md 브라우저 조작이 꺼져 있으면 먼저 켜세요.';
const seen = new Set();
// media_id -> DM text. Override/extend with env var DM_MAP (JSON string) or edit src/dm-map.json.
function dmTextFor(env, mediaId) {
  let map = { ...DM_MAP_FILE };
  try { if (env.DM_MAP) map = { ...map, ...JSON.parse(env.DM_MAP) }; } catch {}
  return (mediaId && map[String(mediaId)]) || DM_TEXT;
}

function text(body, status = 200) {
  return new Response(body, {
    status,
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
  });
}

async function hmacHex(secret, payload) {
  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(payload));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

async function graphPost(path, token, body) {
  const params = new URLSearchParams({ ...body, access_token: token });
  const res = await fetch(`${GRAPH}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`graph ${res.status} ${err.slice(0, 200)}`);
  }
}

async function handleComment(env, commentId, fromId, fromUsername, mediaId) {
  const me = String(env.IG_GRAPH_USER_ID || '');
  if (!commentId) return 'skip';
  if (fromUsername === 'flam__ing') return 'self';
  if (me && String(fromId) === me) return 'self';
  if (seen.has(commentId)) return 'dup';
  seen.add(commentId);
  const token = env.IG_USER_ACCESS_TOKEN;
  if (!token) return 'no_token';
  await graphPost(`/${commentId}/replies`, token, { message: COMMENT_REPLY });
  const ig = env.IG_GRAPH_USER_ID || 'me';
  try {
    await graphPost(`/${ig}/messages`, token, {
      recipient: JSON.stringify({ id: String(fromId) }),
      message: JSON.stringify({ text: dmTextFor(env, mediaId) }),
    });
  } catch {
    return 'replied_dm_err';
  }
  return 'ok';
}

async function onGet(request, env) {
  const url = new URL(request.url);
  const mode = url.searchParams.get('hub.mode') || '';
  const token = url.searchParams.get('hub.verify_token') || '';
  const challenge = url.searchParams.get('hub.challenge') || '';
  if (mode === 'subscribe' && token && token === env.WEBHOOK_VERIFY_TOKEN) {
    return text(challenge);
  }
  return text('forbidden', 403);
}

async function onPost(request, env) {
  const raw = await request.text();
  const secret = env.META_APP_SECRET || '';
  const sig = request.headers.get('X-Hub-Signature-256') || '';
  if (secret) {
    if (!sig.startsWith('sha256=')) return json({ ok: false }, 403);
    const expect = await hmacHex(secret, raw);
    if (expect !== sig.slice(7)) return json({ ok: false }, 403);
  }
  let payload;
  try {
    payload = JSON.parse(raw || '{}');
  } catch {
    return json({ ok: false }, 400);
  }
  const results = [];
  for (const entry of payload.entry || []) {
    for (const ch of entry.changes || []) {
      const val = ch.value || {};
      const cid = String(val.id || '');
      const from = val.from || {};
      results.push(
        await handleComment(env, cid, from.id, from.username, (val.media || {}).id).catch((e) => `err:${e.message}`),
      );
    }
  }
  return json({ ok: true, results });
}

const SKILL_MD = "---\nname: \uc778\uc2a4\ud0c0 \ub313\uae00 \uc790\ub3d9\ub2f5\ndescription: Instagram \ub313\uae00 \uc790\ub3d9\ub2f5+DM\uc744 \uacf5\uc2dd Meta \uc6f9\ud6c5\uacfc Cloudflare Worker\ub85c \ub9cc\ub4e4 \ub54c \uc4f4\ub2e4. \ud3f4\ub9c1 \uae08\uc9c0. Codex/Claude Code\ub294 \ube0c\ub77c\uc6b0\uc800 \uc870\uc791\uc774 \uaebc\uc838 \uc788\uc73c\uba74 \uba3c\uc800 \ucf20\ub2e4.\n---\n# \uc778\uc2a4\ud0c0 \ub313\uae00 \uc790\ub3d9\ub2f5 (\uc6f9\ud6c5 + Cloudflare)\n\n\uc774 \ud30c\uc77c\uc744 \ubc1b\uc544\uc11c Codex \ub610\ub294 Claude Code\uc5d0 \ub4dc\ub798\uadf8\uc564\ub4dc\ub86d \ud558\uba74 \ub41c\ub2e4. \uc138\uc158 \ucfe0\ud0a4 \ud3f4\ub9c1, GitHub Actions \ub313\uae00 \ud6d1\uae30, 30\ucd08/5\ubd84 \ub8e8\ud504\ub294 \uc4f0\uc9c0 \uc54a\ub294\ub2e4.\n\n## \uc774 \uc2a4\ud0ac\uc744 \uc5f0 \uc5d0\uc774\uc804\ud2b8\uc5d0\uac8c\n1. \ube0c\ub77c\uc6b0\uc800 \uc870\uc791\uc774 \ud544\uc218\ub2e4. Meta/Cloudflare \ub85c\uadf8\uc778\uc5d0 \ud544\uc694\ud558\ub2e4.\n   - Claude Code: Chrome/computer-use/\ube0c\ub77c\uc6b0\uc800 MCP\uac00 \uaebc\uc838 \uc788\uc73c\uba74 \uba3c\uc800 \ucf20\ub2e4.\n   - Codex: browser \ub3c4\uad6c\uac00 \uaebc\uc838 \uc788\uc73c\uba74 \uc124\uc815\uc5d0\uc11c \ucf20\ub2e4.\n   - \ube44\ubc00\ubc88\ud638/2FA/\ucea1\ucc28\ub294 \uc0ac\uc6a9\uc790\uac00 \ud55c\ub2e4.\n2. \uacf5\uc2dd Meta \uc6f9\ud6c5\ub9cc \uc4f4\ub2e4. \ub313\uae00\uc744 \uc8fc\uae30\uc801\uc73c\ub85c \uc870\ud68c\ud558\uc9c0 \uc54a\ub294\ub2e4.\n3. \ud638\uc2a4\ud2b8\ub294 Cloudflare Worker (*.workers.dev\uc774\uba74 \ucda9\ubd84). github.io \uae08\uc9c0.\n4. Instagram Login \uc720\uc800 \ud1a0\ud070(IGAA)\uc744 Worker \uc2dc\ud06c\ub9bf\uc73c\ub85c \ub123\ub294\ub2e4. Page \ud1a0\ud070 \ubd88\ud544\uc694.\n5. \uc2dc\ud06c\ub9bf\uc744 \ucc44\ud305/\uae43\uc5d0 \ubd99\uc774\uc9c0 \uc54a\ub294\ub2e4.\n\n## \uae30\ubcf8 \ubb38\uad6c\n- \uacf5\uac1c \ub2f5\uae00: DM \ub4dc\ub838\uc2b5\ub2c8\ub2e4!\n- DM: https://ai-ing.org \uadf8\ub9ac\uace0 \uc774 \uc2a4\ud0ac https://github.com/flam-ing/meta-api-automation/releases/latest/download/SKILL.md\n- \ube0c\ub77c\uc6b0\uc800 \uc870\uc791\uc774 \uaebc\uc838 \uc788\uc73c\uba74 \uba3c\uc800 \ucf1c\uc138\uc694.\n- \uc790\uae30 \ub313\uae00 skip\n\n## \uc21c\uc11c\n1. \ube0c\ub77c\uc6b0\uc800 \ucf1c\uae30\n2. IG Professional\n3. Meta \uc571 + Instagram Login \uad8c\ud55c(basic, manage_comments, manage_messages)\n4. Tester \ucd08\ub300 \uc218\ub77d\n5. \uc720\uc800 \ud1a0\ud070(IGAA ASCII, \ub9c8\uc2a4\ud0b9 \uc810 \uae08\uc9c0)\n6. wrangler login \ud6c4 Worker deploy\n7. GET \ud578\ub4dc\uc170\uc774\ud06c / POST \uc11c\uba85 \uac80\uc99d / \ub2f5\uae00+DM\n8. \uc2dc\ud06c\ub9bf: WEBHOOK_VERIFY_TOKEN, META_APP_SECRET, IG_USER_ACCESS_TOKEN, IG_GRAPH_USER_ID\n9. \ucf5c\ubc31\uc744 Worker URL\ub85c, comments \uad6c\ub3c5, POST /me/subscribed_apps\n10. \ub2e4\ub978 \uacc4\uc815\uc73c\ub85c \ud14c\uc2a4\ud2b8. \ud3f4\ub9c1 \uae08\uc9c0.\n";
export default {
  async fetch(request, env) {
    const path = new URL(request.url).pathname.toLowerCase();
    if (request.method === 'GET' && (path === '/skill.md' || path === '/skill')) {
      return Response.redirect('https://github.com/flam-ing/meta-api-automation/releases/latest/download/SKILL.md', 302);
    }
    if (request.method === 'GET') return onGet(request, env);
    if (request.method === 'POST') return onPost(request, env);
    return text('method', 405);
  },
};
