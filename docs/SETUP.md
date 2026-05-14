# LEA Setup Guide
**Instalare completă pe Windows 10**

---

## Cerințe

- Windows 10 (64-bit)
- Python 3.8+ (`python --version`)
- Browser modern (Edge, Chrome, Firefox)
- 2GB RAM liber minimum (4GB recomandat)
- 700MB spațiu pe disc (model AI inclus)

---

## Instalare rapidă

### 1. Clonează / copiază repo

```batch
xcopy /E /I vv-lea C:\LEA_CORE
```

### 2. Instalează dependențe Python

```batch
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --no-cache-dir
pip install ctransformers huggingface_hub
```

**Dacă pip eșuează (path lung Windows):**
```batch
set TEMP=C:\T & mkdir C:\T
pip install llama-cpp-python --no-cache-dir
rmdir /s /q C:\T
```

### 3. Descarcă modelul AI (opțional — se descarcă automat la prima utilizare)

```batch
local\launchers\download_model.bat
```

Sau modelul se descarcă automat (~345MB) la primul click "Ask Lea".

### 4. Pornire

```batch
local\launchers\LEA_START.bat
```

Deschide browser la `http://localhost:9999/`

---

## Structura fișiere după instalare

```
C:\LEA_CORE\
├── core\servers\pairing_server.py   → serverul principal
├── core\ai\lea_llm.py               → TinyLlama
├── data\models\tinyllama.gguf       → model AI (~480MB)
├── data\logs\development_journal.md → jurnal automat
├── interface\workspace\index.html   → UI principal
└── interface\control_panel.html     → aprobare acțiuni
```

```
C:\LEA_PRIVAT\
├── rafturi\*.json     → knowledge base Lea
└── active\context.txt → context curent (editat de tine)
```

```
Desktop\LEA_OBSERVER\context.txt  → context rapid
```

---

## Troubleshooting

| Problemă | Soluție |
|----------|---------|
| Server nu pornește | Verifică `python --version` în CMD |
| Port 9999 ocupat | Rulează `STOP_LEA.bat`, apoi `LEA_START.bat` |
| Model nu se încarcă | Prima utilizare descarcă ~345MB — așteaptă |
| "Entry not found" model | Rulează `download_model.bat` |
| pip install eșuează | Folosește `set TEMP=C:\T` înainte de pip |

---

## Verificare instalare

```python
# Rulează în CMD:
python -c "from llama_cpp import Llama; print('OK')"
python -c "from ctransformers import AutoModelForCausalLM; print('OK')"
```

```batch
:: Verifică server:
python C:\LEA_CORE\core\servers\pairing_server.py
:: Deschide http://localhost:9999/status
```
