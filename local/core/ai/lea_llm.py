import os
import json
import struct
import threading

LEA_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check multiple candidate paths; C:\LEA_CORE is the primary install location
_MODEL_CANDIDATES = [
    r'C:\LEA_CORE\data\models\tinyllama.gguf',
    os.path.join(LEA_ROOT, 'data', 'models', 'tinyllama.gguf'),
    os.path.join(os.path.expanduser('~'), 'LEA_CORE', 'data', 'models', 'tinyllama.gguf'),
]
MODEL_PATH = next(
    (p for p in _MODEL_CANDIDATES if os.path.isfile(p)),
    _MODEL_CANDIDATES[0]
)

# Surse de context (ordine de prioritate)
CONTEXT_PATHS = [
    os.path.join('C:\\', 'LEA_PRIVAT', 'active', 'context.txt'),
    os.path.join(os.path.expanduser('~'), 'Desktop', 'LEA_OBSERVER', 'context.txt'),
]
RAFT_DIRS = [
    os.path.join('C:\\', 'LEA_PRIVAT', 'rafturi'),
    os.path.join(LEA_ROOT, 'data', 'rafturile'),
]

_llm = None
_backend = None   # 'llama-cpp' | 'ctransformers'
_loading = False
_load_error = None
_lock = threading.Lock()


def _is_valid_gguf(path):
    if not os.path.isfile(path):
        return False
    if os.path.getsize(path) < 50_000_000:
        return False
    with open(path, 'rb') as f:
        magic = f.read(4)
        ver = struct.unpack('<I', f.read(4))[0]
    return magic == b'GGUF' and ver <= 3


def get_status():
    if _llm is not None:
        return 'ready'
    if _loading:
        return 'loading'
    if _load_error:
        return f'error: {_load_error}'
    if not _is_valid_gguf(MODEL_PATH):
        return 'model_missing'
    return 'not_loaded'


def load_model_async():
    global _llm, _loading, _load_error, _backend
    with _lock:
        if _llm is not None or _loading:
            return
        _loading = True

    def _load():
        global _llm, _loading, _load_error, _backend

        print(f'[LEA AI] MODEL_PATH rezolvat la: {MODEL_PATH}')
        print(f'[LEA AI] Fisier exista: {os.path.isfile(MODEL_PATH)}')
        print(f'[LEA AI] GGUF valid: {_is_valid_gguf(MODEL_PATH)}')

        # --- METODA 1: llama-cpp-python cu fisier local valid ---
        if _is_valid_gguf(MODEL_PATH):
            try:
                from llama_cpp import Llama
                print('[LEA AI] [M1] Loading local GGUF cu llama-cpp...')
                _llm = Llama(
                    model_path=MODEL_PATH,
                    n_ctx=2048,
                    n_threads=2,
                    n_gpu_layers=0,
                    verbose=False
                )
                _backend = 'llama-cpp'
                _load_error = None
                print('[LEA AI] [M1] llama-cpp OK')
                _loading = False
                return
            except Exception as e:
                print(f'[LEA AI] [M1] llama-cpp local fail: {e}')

        # --- METODA 2: llama-cpp from_pretrained (download automat) ---
        try:
            from llama_cpp import Llama
            print('[LEA AI] [M2] Download model de pe HuggingFace cu llama-cpp...')
            _llm = Llama.from_pretrained(
                repo_id='TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF',
                filename='*Q2_K*.gguf',
                n_ctx=2048,
                n_threads=2,
                n_gpu_layers=0,
                verbose=False,
                cache_dir=os.path.join(LEA_ROOT, 'data', 'models')
            )
            _backend = 'llama-cpp'
            _load_error = None
            print('[LEA AI] [M2] llama-cpp from_pretrained OK')
            _loading = False
            return
        except Exception as e:
            print(f'[LEA AI] [M2] llama-cpp from_pretrained fail: {e}')

        # --- METODA 3: ctransformers cu fisier local ---
        if _is_valid_gguf(MODEL_PATH):
            try:
                from ctransformers import AutoModelForCausalLM
                print('[LEA AI] [M3] Loading local GGUF cu ctransformers...')
                _llm = AutoModelForCausalLM.from_pretrained(
                    MODEL_PATH, model_type='llama'
                )
                _backend = 'ctransformers'
                _load_error = None
                print('[LEA AI] [M3] ctransformers local OK')
                _loading = False
                return
            except Exception as e:
                print(f'[LEA AI] [M3] ctransformers local fail: {e}')

        # --- METODA 4: ctransformers download HuggingFace ---
        try:
            from ctransformers import AutoModelForCausalLM
            print('[LEA AI] [M4] Download model de pe HuggingFace cu ctransformers...')
            _llm = AutoModelForCausalLM.from_pretrained(
                'TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF',
                model_file='tinyllama-1.1b-chat-v1.0.Q2_K.gguf',
                model_type='llama'
            )
            _backend = 'ctransformers'
            _load_error = None
            print('[LEA AI] [M4] ctransformers from HF OK')
            _loading = False
            return
        except Exception as e:
            print(f'[LEA AI] [M4] ctransformers HF fail: {e}')
            _load_error = 'Modelul se pregateste... (~10-30 sec prima data)'

        _loading = False

    threading.Thread(target=_load, daemon=True).start()


def _load_context():
    for path in CONTEXT_PATHS:
        if os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read(600).strip()
                if content and not content.startswith('#'):
                    return content
                # Returneaza si daca are linii non-comment
                lines = [l for l in content.splitlines() if l.strip() and not l.startswith('#')]
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
                parts.append(f'[{fname}]: {json.dumps(data, ensure_ascii=False)[:500]}')
            except Exception:
                pass
        if parts:
            break  # Foloseste primul director cu date
    return '\n'.join(parts[:6])


def _generate(prompt):
    if _backend == 'llama-cpp':
        result = _llm(
            prompt,
            max_tokens=256,
            temperature=0.7,
            top_p=0.9,
            stop=['</s>', '<|user|>', '<|system|>'],
            echo=False
        )
        return result['choices'][0]['text'].strip()
    elif _backend == 'ctransformers':
        return _llm(
            prompt,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.9,
            stop=['</s>', '<|user|>']
        ).strip()
    raise RuntimeError('No backend loaded')


def ask(question, extra_context=''):
    global _llm

    if _llm is None:
        status = get_status()
        if status in ('model_missing', 'not_loaded'):
            load_model_async()
            return None, 'loading'
        return None, status

    system = (
        'Esti LEA, asistentul AI personal al lui Cosmin Toma, CEO VV Hybrid Universe. '
        'Raspunzi concis, clar, in romana sau engleza dupa cum intreaba. '
        'VV Hybrid Universe: companie tech, suveranitate digitala, AI local, privacy totala.'
    )

    raft = _load_rafturi()
    if raft:
        system += f'\n\nCunostinte:\n{raft[:1500]}'

    ctx = _load_context()
    if ctx:
        system += f'\n\nContext curent Cosmin: {ctx}'

    if extra_context:
        system += f'\n\n{extra_context}'

    prompt = f'<|system|>\n{system}</s>\n<|user|>\n{question}</s>\n<|assistant|>\n'

    try:
        answer = _generate(prompt)
        return answer, 'ok'
    except Exception as e:
        return None, f'error: {e}'
