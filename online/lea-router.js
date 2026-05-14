// LEA Router — Detecție automată Local vs Online, unified API
// VV Hybrid Universe · Cosmin Toma

const LeaRouter = (function () {
  const LOCAL_URL = 'http://localhost:9999';
  const TIMEOUT_MS = 3000;

  let _mode = 'unknown';      // 'local' | 'online' | 'demo'
  let _sessionId = null;
  let _paired = false;

  // ── Detectare mod ──────────────────────────────────────────────
  async function detect() {
    try {
      const r = await fetch(LOCAL_URL + '/status', {
        signal: AbortSignal.timeout(TIMEOUT_MS)
      });
      if (r.ok) {
        const d = await r.json();
        _mode = 'local';
        _paired = d.paired;
        return 'local';
      }
    } catch {}
    _mode = 'online';
    return 'online';
  }

  // ── Pairing automat (pentru workspace) ─────────────────────────
  async function ensurePaired() {
    if (_sessionId) return true;
    if (_mode !== 'local') return false;

    try {
      const r1 = await fetch(LOCAL_URL + '/generate_code');
      const d1 = await r1.json();

      const r2 = await fetch(LOCAL_URL + '/pair', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: d1.code })
      });
      const d2 = await r2.json();

      if (d2.success) { _sessionId = d2.session_id; return true; }
    } catch {}
    return false;
  }

  // ── Ask Lea ─────────────────────────────────────────────────────
  async function ask(question) {
    // Cache check
    const cached = LeaCache.getCache(question);
    if (cached) return { success: true, answer: cached, fromCache: true };

    if (_mode === 'local') {
      try {
        const r = await fetch(LOCAL_URL + '/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question })
        });
        const d = await r.json();
        if (d.success) LeaCache.saveCache(question, d.answer);
        return d;
      } catch (e) {
        return { success: false, error: 'network', message: e.message };
      }
    }

    // Online mode — placeholder (viitor: cloud API)
    return {
      success: false,
      error: 'online_not_configured',
      message: 'Mod online necesită server cloud. Porneste LEA_START.bat pentru mod local.'
    };
  }

  // ── Execute comandă ──────────────────────────────────────────────
  async function execute(command) {
    if (_mode !== 'local') return { success: false, error: 'local_required' };

    await ensurePaired();
    if (!_sessionId) return { success: false, error: 'not_paired' };

    const r = await fetch(LOCAL_URL + '/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: _sessionId, command })
    });
    return await r.json();
  }

  // ── Status server ────────────────────────────────────────────────
  async function status() {
    if (_mode !== 'local') return null;
    try {
      const r = await fetch(LOCAL_URL + '/status', { signal: AbortSignal.timeout(2000) });
      return await r.json();
    } catch { return null; }
  }

  // ── Getteri ──────────────────────────────────────────────────────
  return {
    detect, ensurePaired, ask, execute, status,
    mode: () => _mode,
    isLocal: () => _mode === 'local',
    sessionId: () => _sessionId
  };
})();
