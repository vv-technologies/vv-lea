@echo off
title LEA - Oprire...
color 0C

echo.
echo  ============================================
echo   LEA WORKSPACE - Oprire
echo  ============================================
echo.

:: Opreste serverul Python pe portul 9999
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":9999" ^| findstr "LISTENING"') do (
    echo  [..] Opresc procesul PID: %%a
    taskkill /PID %%a /F >nul 2>&1
)

echo  [OK] LEA Server oprit.
echo.

timeout /t 2 /nobreak >nul
exit
