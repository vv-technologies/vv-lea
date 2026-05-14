@echo off
title LEA - TinyLlama Setup
color 0A

echo.
echo  ============================================
echo   LEA - TinyLlama Setup
echo   VV Hybrid Universe
echo  ============================================
echo.

:: FIX Windows path prea lung — redirectam TEMP la C:\T
if not exist "C:\T\" mkdir "C:\T\"
set TEMP=C:\T
set TMP=C:\T
echo  [FIX] TEMP redirectat la C:\T (fix Windows path limit)
echo.

:: Verifica Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERR] Python nu e instalat sau nu e in PATH!
    pause & exit /b 1
)

echo  [1/4] Incercare 1: wheel precompilat CPU (fara compilare)...
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --no-cache-dir -q
if %errorlevel% == 0 goto :SUCCESS

echo  [WARN] Metoda 1 esuata. Incercare 2: install standard cu --no-cache-dir...
pip install llama-cpp-python --no-cache-dir -q
if %errorlevel% == 0 goto :SUCCESS

echo  [WARN] Metoda 2 esuata. Incercare 3: install --user...
pip install llama-cpp-python --user --no-cache-dir -q
if %errorlevel% == 0 goto :SUCCESS

echo.
echo  [ERR] Toate metodele automate au esuat.
echo  Incearca manual in CMD (ca Administrator):
echo.
echo    reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f
echo    (restart PC, apoi reporneste acest script)
echo.
goto :CHECK_MODEL

:SUCCESS
echo.
echo  [OK] llama-cpp-python instalat cu succes!

:CHECK_MODEL
echo.
echo  [2/4] Verificare model...
if exist "C:\LEA_CORE\data\models\tinyllama.gguf" (
    echo  [OK] Model gasit: C:\LEA_CORE\data\models\tinyllama.gguf
    goto :DONE
)

echo  [3/4] Model lipsa — descarca manual:
echo.
echo   URL: https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/tree/main
echo.
echo   Alege fisierul (unul dintre):
echo     TinyLlama-1.1B-Chat-v1.0.Q3_K_S.gguf   ~480MB  RECOMANDAT
echo     TinyLlama-1.1B-Chat-v1.0.Q2_K.gguf      ~345MB  mai mic
echo.
echo   Salveaza-l exact aici:
echo     C:\LEA_CORE\data\models\tinyllama.gguf
echo.

:DONE
echo  [4/4] Curatare temp...
rmdir /s /q "C:\T" >nul 2>&1

echo.
echo  ============================================
echo   Gata! Porneste LEA_START.bat
echo   Deschide http://localhost:9999/
echo   Click "Ask Lea" — modelul se incarca ~15s
echo  ============================================
echo.
pause
