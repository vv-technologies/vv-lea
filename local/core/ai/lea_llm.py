import os
import json
import time
import threading
import urllib.request
import urllib.error

LEA_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RAFT_DIRS = [
    os.path.join('C:\\', 'LEA_PRIVAT', 'rafturi'),
    os.path.join(LEA_ROOT, 'data', 'rafturile'),
]
CONTEXT_PATHS = [
    os.path.join('C:\\', 'LEA_PRIVAT', 'active', 'context.txt'),
    os.path.join(os.path.expanduser('~'), 'Desktop', 'LEA_OBSERVER', 'context.txt'),
]

_cache = {}
_cache_lock = threading.Lock()
CACHE_TTL = 3600

SIMPLE_TRIGGERS = [
    'cine ești', 'cine esti', 'ce ești', 'ce esti',
    'ce poți', 'ce poti', 'ce faci', 'ce mai faci',
    'help', 'ajutor', 'salut', 'bună', 'buna', 'hello', 'hi',
]

LOCAL_RESPONSES = {
    'cine ești':  'Sunt LEA — orchestratorul AI al VV Hybrid Universe. Execut comenzi local și răspund la întrebări complexe prin Gemini. Privacy totală, control total.',
    'cine esti':  'Sunt LEA — orchestratorul AI al VV Hybrid Universe. Execut comenzi local și răspund la întrebări complexe prin Gemini. Privacy totală, control total.',
    'ce poți':    'Pot executa comenzi locale (creare/citire fișiere), răspunde la orice întrebare prin Gemini, și funcționez offline cu cache. Spune-mi ce ai nevoie!',
    'ce poti':    'Pot executa comenzi locale (creare/citire fișiere), răspunde la orice întrebare prin Gemini, și funcționez offline cu cache. Spune-mi ce ai nevoie!',
    'help':       'Comenzi: "creează fișier X", "citește X". Întrebări complexe: direct prin Gemini. Cache instant pentru repetiții.',
    'ajutor':     'Cu ce te ajut? Spune-mi ce vrei să fac.',
    'salut':      'Salut! Sunt LEA. Cu ce te ajut?',
    'bună':       'Bună! Sunt LEA. Cu ce te pot ajuta?',
    'buna':       'Bună! Sunt LEA. Cu ce te pot ajuta?',
    'hello':      "Hello! I'm LEA, your VV assistant. What do you need?",
    'hi':         "Hi! LEA here. How can I help?",
    'ce faci':    'Funcționez perfect! Aștept întrebări sau comenzi.',
    'ce mai faci':'Funcționez perfect! Aștept întrebări sau comenzi.',
}


def _get_cache(question):
    with _cache_lock:
        entry = _cache.get(question.lower().strip())
        if entry and time.time() - entry['ts'] < CACHE_TTL:
            return entry['answer'], entry['source']
    return None, None


def _set_cache(question, answer, source):
    with _cache_lock:
        _cache[question.lower().strip()] = {'answer': answer, 'source': source, 'ts': time.time()}
        if len(_cache) > 200:
            oldest = min(_cache, key=lambda k: _cache[k]['ts'])
            del _cache[oldest]


def _is_simple(question):
    q = question.lower().strip()
    return any(t in q for t in SIMPLE_TRIGGERS)


def _local_response(question):
    q = question.lower().strip()
    for key, answer in LOCAL_RESPONSES.items():
        if key in q:
            return answer
    return 'Încearcă: "Cine ești?", "Ce poți face?" sau orice întrebare complexă!'


def _load_context():
    for path in CONTEXT_PATHS:
        if os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = [l for l in f.read(600).splitlines() if l.strip() and not l.startswith('#')]
                if lines:
                    return '\n'.join(lines[:5])
            except Exception:
                pass
    return ''


def _load_rafturi():
    parts = []
    for raft_dir in RAFT_DIRS:
        if not os.path.isdir(raft_dir):
            continue
        for fname in sorted(os.listdir(raft_dir)):
            if not fname.endswith('.json'):
                continue
            try:
                with open(os.path.join(raft_dir, fname), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                parts.append(f'[{fname}]: {json.dumps(data, ensure_ascii=False)[:400]}')
            except Exception:
                pass
        if parts:
            break
    return '\n'.join(parts[:6])


def _ask_gemini(question, extra_context=''):
    key = os.getenv('GEMINI_API_KEY', '')
    if not key:
        return None, 'no_key'

    system = (
        'Ești LEA, asistentul AI personal al lui Cosmin Toma, CEO VV Hybrid Universe. '
        'Răspunzi concis și clar, în română sau engleză după cum întreabă utilizatorul. '
        'VV Hybrid Universe: companie tech, suveranitate digitală, AI local, privacy totală.'
    )

    raft = _load_rafturi()
    if raft:
        system += f'\n\nCunoștințe din rafturi:\n{raft[:1000]}'

    ctx = _load_context()
    if ctx:
        system += f'\n\nContext curent Cosmin: {ctx}'

    if extra_context:
        system += f'\n\n{extra_context}'

    full_prompt = f'{system}\n\nÎntrebare: {question}'

    payload = json.dumps({
        'contents': [{'role': 'user', 'parts': [{'text': full_prompt}]}],
        'generationConfig': {'temperature': 0.7, 'maxOutputTokens': 512}
    }).encode('utf-8')

    url = (
        'https://generativelanguage.googleapis.com/v1beta/models/'
        f'gemini-2.0-flash:generateContent?key={key}'
    )

    try:
        req = urllib.request.Request(
            url, data=payload, headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode('utf-8'))
        text = result['candidates'][0]['content']['parts'][0]['text'].strip()
        return text, 'gemini'
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')[:200]
        print(f'[LEA AI] Gemini HTTP {e.code}: {body}')
        return None, f'gemini_http_{e.code}'
    except Exception as e:
        print(f'[LEA AI] Gemini fail: {e}')
        return None, f'gemini_error'


def ask(question, extra_context=''):
    """Returns (answer, status, source) — source: 'cache' | 'local' | 'gemini'"""
    q = question.strip()

    cached_answer, cached_source = _get_cache(q)
    if cached_answer:
        return cached_answer, 'ok', 'cache'

    if _is_simple(q):
        answer = _local_response(q)
        _set_cache(q, answer, 'local')
        return answer, 'ok', 'local'

    t0 = time.time()
    answer, source = _ask_gemini(q, extra_context)
    if answer:
        _set_cache(q, answer, 'gemini')
        print(f'[LEA AI] Gemini OK ({int((time.time()-t0)*1000)}ms)')
        return answer, 'ok', 'gemini'

    if source == 'no_key':
        fallback = (
            'Pentru răspunsuri complexe, adaugă variabila de mediu GEMINI_API_KEY. '
            'Încearcă întrebări simple: "Cine ești?", "Ce poți?"'
        )
        return fallback, 'ok', 'local'

    return None, source, 'error'


def get_status():
    key = os.getenv('GEMINI_API_KEY', '')
    return 'gemini_ready' if key else 'no_api_key'
