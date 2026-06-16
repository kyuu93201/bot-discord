@echo off
title He Thong Auto Bot va Rich Presence C++
cls

set COMPILER_PATH=C:\MinGW\bin
set PATH=%COMPILER_PATH%;%PATH%

echo [.] Dang kiem tra moi truong he thong...
g++ --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [X] Loi: Khong tim thay trinh bien dich g++ tai %COMPILER_PATH%
    pause
    exit
)

echo [.] Dang build ma nguon main.cpp sang rpc_discord.exe...
:: SỬ DỤNG -mthreads ĐỂ SỬA LỖI CANNOT FIND -LPTHREAD
g++ main.cpp -o rpc_discord.exe -I. -L. -ldiscord-rpc -mthreads

if %ERRORLEVEL% NEQ 0 (
    echo [X] Loi: Vui long kiem tra lai code main.cpp!
    pause
    exit
)
echo [+=] Bien dich Rich Presence C++ thanh cong!
echo --------------------------------------------------

echo [.] Dang kiem tra va tu dong cai dat thu vien discord.py va requests...
python -m pip install discord.py requests >nul 2>&1

echo [*] Dang khoi dong Bot Tu (Chay cua so rieng)...
start "Discord Bot Online" cmd /k python bot.py

echo [*] Dang khoi dong Rich Presence C++...
echo [!] He thong da hoat dong. Giu cua so nay de duy tri sanh cho!
echo --------------------------------------------------

rpc_discord.exe

pause