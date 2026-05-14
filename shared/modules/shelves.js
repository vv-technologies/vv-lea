// LEA Shelves — Sistem de rafturi (knowledge base local, persistat în localStorage)
// VV Hybrid Universe · Cosmin Toma

const LeaShelves = (function () {
  const STORAGE_KEY = 'lea_shelves_v1';

  function _read() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); }
    catch { return {}; }
  }

  function _write(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }

  // Citeste un raft
  function get(key) {
    const all = _read();
    return all[key] ? all[key].value : null;
  }

  // Salveaza un raft
  function set(key, value) {
    const all = _read();
    all[key] = { value, updatedAt: Date.now() };
    _write(all);
  }

  // Sterge un raft
  function remove(key) {
    const all = _read();
    delete all[key];
    _write(all);
  }

  // Lista toate rafturile
  function list() {
    return Object.entries(_read()).map(([key, v]) => ({
      key,
      preview: JSON.stringify(v.value).substring(0, 60),
      updatedAt: new Date(v.updatedAt).toLocaleString('ro-RO')
    }));
  }

  // Import din JSON extern (ex: LEA_PRIVAT/rafturi/*.json)
  function importJson(key, jsonString) {
    try {
      const value = JSON.parse(jsonString);
      set(key, value);
      return true;
    } catch { return false; }
  }

  // Export tot ca JSON descarcabil
  function exportAll() {
    const blob = new Blob([JSON.stringify(_read(), null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'lea_shelves_backup.json';
    a.click();
  }

  // Goleste toate rafturile
  function clear() { localStorage.removeItem(STORAGE_KEY); }

  // Toate datele brute (pentru debug)
  function getAll() { return _read(); }

  return { get, set, remove, list, importJson, exportAll, clear, getAll };
})();

if (typeof module !== 'undefined') module.exports = LeaShelves;
