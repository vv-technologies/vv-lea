@echo off
title LEA - Download Model (Binary Safe)
color 0A

echo.
echo  ============================================
echo   LEA - Download TinyLlama (Binary Safe)
echo   VV Hybrid Universe
echo  ============================================
echo.

set MODEL_DIR=C:\LEA_CORE\data\models
set MODEL_FILE=%MODEL_DIR%\tinyllama.gguf
set MODEL_URL=https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q3_K_S.gguf

if not exist "%MODEL_DIR%\" mkdir "%MODEL_DIR%\"

:: Sterge modelul vechi corupt (daca exista)
if exist "%MODEL_FILE%" (
    echo  [..] Sterg model vechi corupt...
    del /f "%MODEL_FILE%"
    echo  [OK] Sters.
    echo.
)

echo  [..] Descarcare model cu curl (binary mode)...
echo  URL: %MODEL_URL%
echo  Dest: %MODEL_FILE%
echo.
echo  Astept - 477MB, poate dura 5-30 min...
echo.

:: curl.exe (nu alias PowerShell!) = garantat binary mode
C:\Windows\System32\curl.exe ^
  --location ^
  --output "%MODEL_FILE%" ^
  --progress-bar ^
  --retry 3 ^
  --retry-delay 5 ^
  "%MODEL_URL%"

if %errorlevel% neq 0 (
    echo.
    echo  [ERR] Download esuat. Verifica conexiunea si incearca din nou.
    pause & exit /b 1
)

echo.
echo  [..] Verific integritatea fisierului...
python -c @"
import struct, sys
with open(r'C:\LEA_CORE\data\models\tinyllama.gguf', 'rb') as f:
    magic = f.read(4)
    ver = struct.unpack('<I', f.read(4))[0]
if magic == b'GGUF' and ver <= 3:
    print('  [OK] GGUF valid, versiune', ver)
    sys.exit(0)
else:
    print('  [ERR] Fisier invalid! Magic:', magic, 'Version:', ver)
    sys.exit(1)
"@

if %errorlevel% neq 0 (
    echo  [ERR] Fisierul descarcat e invalid. Incearca din nou.
    pause & exit /b 1
)

echo.
echo  ============================================
echo   Download complet si verificat!
echo   Reporneste LEA_START.bat
echo   Ask Lea va fi activ in ~15 secunde.
echo  ============================================
echo.
pause
