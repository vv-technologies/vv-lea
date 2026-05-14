// LEA Cache — Cache local pentru răspunsuri Lea (reduce latența, funcționează offline)
// VV Hybrid Universe · Cosmin Toma

const LeaCache = (function () {
  const STORAGE_KEY = 'lea_cache_v1';
  const DEFAULT_TTL = 24 * 60 * 60 * 1000;  // 24 ore
  const MAX_ENTRIES = 100;

  function _hash(str) {
    let h = 0;
    for (let i = 0; i < str.length; i++) {
      h = (Math.imul(31, h) + str.charCodeAt(i)) | 0;
    }
    return Math.abs(h).toString(36);
  }

  function _read() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); }
    catch { return {}; }
  }

  function _write(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }

  // Cauta raspuns in cache
  function getCache(question, ttl = DEFAULT_TTL) {
    const cache = _read();
    const key = _hash(question.toLowerCase().trim());
    const entry = cache[key];
    if (!entry) return null;
    if (Date.now() - entry.ts > ttl) { _evict(key); return null; }
    entry.hits = (entry.hits || 0) + 1;
    _write(cache);
    return entry.answer;
  }

  // Salveaza raspuns in cache
  function saveCache(question, answer) {
    const cache = _read();
    const key = _hash(question.toLowerCase().trim());
    cache[key] = { answer, question, ts: Date.now(), hits: 0 };

    // Eviction LRU daca depasim MAX_ENTRIES
    const keys = Object.keys(cache);
    if (keys.length > MAX_ENTRIES) {
      const oldest = keys.sort((a, b) => (cache[a].ts || 0) - (cache[b].ts || 0))[0];
      delete cache[oldest];
    }
    _write(cache);
  }

  // Sterge o intrare din cache
  function _evict(key) {
    const cache = _read();
    delete cache[key];
    _write(cache);
  }

  // Sterge cache pentru o intrebare specifica
  function removeCache(question) {
    _evict(_hash(question.toLowerCase().trim()));
  }

  // Goleste tot cache-ul
  function clearCache() { localStorage.removeItem(STORAGE_KEY); }

  // Statistici
  function stats() {
    const cache = _read();
    const entries = Object.values(cache);
    return {
      count: entries.length,
      totalHits: entries.reduce((s, e) => s + (e.hits || 0), 0),
      oldest: entries.length ? new Date(Math.min(...entries.map(e => e.ts))).toLocaleString('ro-RO') : null,
      sizekb: Math.round(JSON.stringify(cache).length / 1024)
    };
  }

  return { getCache, saveCache, removeCache, clearCache, stats };
})();

if (typeof module !== 'undefined') module.exports = LeaCache;
