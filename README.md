# LEA — Local Execution Agent
**VV Hybrid Universe · Cosmin Toma, CEO**

> Primul AI care lucrează **direct** pe laptopul tău. 100% local. Zero cloud. Zero copy-paste.

---

## Ce este LEA?

LEA elimină "postașul" — nu mai copiezi între AI și calculator. Claude trimite comanda, LEA o execută direct pe sistemul tău.

```
Cosmin → Claude → LEA Server → Sistem local
              ↑_____________________↓
```

---

## Quick Start — 3 pași

```batch
1. Dublu-click: local\launchers\LEA_START.bat
2. Browser:     http://localhost:9999/
3. Execute:     paste format LEA → click Execute
```

---

## Structură

```
vv-lea/
├── online/          → Versiune web (standalone, PWA-ready)
│   ├── lea-router.js  → Detecție local vs online, unified API
│   └── manifest.json  → PWA manifest
│
├── local/           → Backend Python (rulează pe laptop)
│   ├── core/
│   │   ├── servers/pairing_server.py  → Server principal (port 9999)
│   │   └── ai/lea_llm.py             → TinyLlama integration
│   └── launchers/   → .bat scripts pentru Windows
│
├── shared/          → Module comune (local + online)
│   └── modules/
│       ├── shelves.js  → Knowledge base local (localStorage)
│       ├── voice.js    → Web Speech API (mic + TTS)
│       └── cache.js    → Cache răspunsuri (offline-ready)
│
└── docs/            → Documentație
    ├── ARCHITECTURE.md
    ├── SETUP.md
    └── DEMO.md
```

---

## Format comandă LEA

```
### LEA_EXECUTE ###
COMENZI = [
    {'type': 'CREATE_FILE', 'path': 'C:\\LEA_CORE\\data\\test.txt', 'content': 'Hello LEA!'},
    {'type': 'READ_FILE', 'path': 'C:\\LEA_CORE\\data\\test.txt'},
    {'type': 'LIST_DIR', 'path': 'C:\\LEA_CORE\\data'}
]
```

---

## Ask Lea (TinyLlama local)

```javascript
// Browser
LeaRouter.detect().then(() => LeaRouter.ask('Ce este VV Hybrid Universe?'));

// Sau direct la server
POST http://localhost:9999/ask
{ "question": "Ce faci LEA?" }
```

---

## Hardware necesar

| Componenta | Minim | Testat pe |
|-----------|-------|-----------|
| OS | Windows 10 | Windows 10 Pro |
| RAM | 2GB | 4GB |
| Storage | 1GB | SSD |
| Python | 3.8+ | 3.12.3 |

**RAM usage:** ~38MB server + ~480MB TinyLlama = ~520MB total

---

## Licență

VV Hybrid Universe © 2026 · Cosmin Toma
