@echo off
title LEA Workspace - Starting...
color 0A

echo.
echo  ============================================
echo   LEA WORKSPACE - VV Hybrid Universe
echo  ============================================
echo.

:: Verifica daca server-ul ruleaza deja pe portul 9999
netstat -ano | findstr ":9999" | findstr "LISTENING" >nul 2>&1
if %errorlevel% == 0 (
    echo  [OK] Server LEA este deja activ.
    goto :OPEN_INTERFACE
)

:: Verifica Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERR] Python nu este instalat sau nu e in PATH!
    echo  Instaleaza Python de la python.org
    pause
    exit /b 1
)

echo  [..] Pornesc LEA Pairing Server...
start "" /min pythonw.exe "C:\LEA_CORE\core\servers\pairing_server.py"

:: Asteapta sa porneasca
timeout /t 2 /nobreak >nul

:: Verifica daca a pornit
netstat -ano | findstr ":9999" | findstr "LISTENING" >nul 2>&1
if %errorlevel% neq 0 (
    echo  [WARN] Server nu a pornit cu pythonw, incerc python normal...
    start "" /min python.exe "C:\LEA_CORE\core\servers\pairing_server.py"
    timeout /t 2 /nobreak >nul
)

echo  [OK] Server LEA pornit pe portul 9999.

:OPEN_INTERFACE
echo  [..] Deschid Masa de Lucru...
start "" "http://localhost:9999/"

timeout /t 1 /nobreak >nul
echo.
echo  ============================================
echo   LEA Workspace ACTIVE!
echo   http://localhost:9999
echo  ============================================
echo.

timeout /t 3 /nobreak >nul
exit
