# LEA Architecture
**VV Hybrid Universe · Technical Reference**

---

## System Overview

```
┌─────────────────────────────────────────────────────┐
│                    BROWSER (User)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  Workspace   │  │ Control Panel│  │ Ask Lea  │  │
│  │ /index.html  │  │/control_panel│  │  Modal   │  │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘  │
└─────────┼─────────────────┼───────────────┼─────────┘
          │ HTTP/JSON        │               │
          ▼                 ▼               ▼
┌─────────────────────────────────────────────────────┐
│          pairing_server.py (port 9999)              │
│                                                     │
│  GET  /            → workspace/index.html           │
│  GET  /status      → server state                   │
│  GET  /generate_code → pairing code                 │
│  POST /pair        → session creation               │
│  POST /execute     → run command (Manual/Auto)      │
│  POST /approve     → approve pending action         │
│  POST /ask         → TinyLlama query                │
│  GET  /ask_status  → model loading state            │
└─────────────────────────────────────────────────────┘
          │                               │
          ▼                               ▼
┌──────────────────┐           ┌──────────────────────┐
│  File System     │           │   lea_llm.py          │
│  (CREATE, READ,  │           │  ┌─────────────────┐ │
│   LIST_DIR)      │           │  │ TinyLlama 1.1B  │ │
└──────────────────┘           │  │ llama-cpp-python│ │
                               │  │ ctransformers   │ │
                               │  └─────────────────┘ │
                               └──────────────────────┘
```

---

## Componente

### pairing_server.py
- HTTP server pe `localhost:9999`
- Servește fișiere statice din `interface/`
- Gestionează sesiuni (pairing code → session_id)
- Execută comenzi în mod Manual (cu aprobare) sau Auto
- Proxy la lea_llm.py pentru Ask Lea
- CORS headers pentru acces browser

### lea_llm.py
- Lazy loading (modelul se încarcă la primul /ask)
- 4 metode de loading în cascadă:
  1. Local GGUF valid → llama-cpp-python
  2. HuggingFace download → llama-cpp `from_pretrained`
  3. Local GGUF → ctransformers
  4. HuggingFace download → ctransformers
- Context automat din `LEA_PRIVAT/rafturi/` și `LEA_OBSERVER/context.txt`
- Chat format TinyLlama: `<|system|>...<|user|>...<|assistant|>`

### shared/modules/shelves.js
- Knowledge base persistent în localStorage
- Import/export JSON
- CRUD simplu: get/set/remove/list

### shared/modules/voice.js
- Web Speech API (browser built-in, zero dependențe externe)
- startMic / stopMic / toggleMic
- Text-to-Speech cu preferință voce română

### shared/modules/cache.js
- Cache răspunsuri Lea în localStorage
- TTL 24h, max 100 intrări (LRU eviction)
- Hash-based key (MD-style, fără crypto)

### lea-router.js
- Auto-detectare mod: local (localhost:9999) vs online
- Unified API: `ask()`, `execute()`, `status()`
- Cache integration (servește din cache dacă există)

---

## Security Model

```
Browser ←──CORS──→ localhost:9999 (nu e expus extern)
                        │
              Pairing Protocol:
              1. generate_code() → cod 6 cifre
              2. pair(cod) → session_id
              3. execute(session_id, cmd) → validare sesiune
              4. Manual mode: cmd → pending → aprobare umana
```

---

## Data Flow — Execute Command

```
1. User paste LEA_EXECUTE format în Workspace
2. JS parsează COMENZI = [...]
3. ensurePaired() → obține session_id
4. POST /execute { session_id, command }
5a. Auto mode → execute_command() → file system
5b. Manual mode → pending_actions[] → Control Panel → Approve
6. Response JSON → Preview tab
```

---

## Data Flow — Ask Lea

```
1. User scrie întrebare în modal
2. LeaCache.getCache(question) → dacă există, return imediat
3. POST /ask { question }
4. server verifică model status:
   - not_loaded → load_model_async() → return 'loading'
   - loading → return 'loading' (user retry)
   - ready → generate(prompt)
5. Prompt format:
   <|system|> LEA identity + rafturi + context </s>
   <|user|> question </s>
   <|assistant|>
6. Response → client → LeaCache.saveCache()
```
