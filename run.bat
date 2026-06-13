@echo off
title He Thong Auto Bot va Rich Presence C++
cls

:: ==========================================
:: CONFIG ĐƯỜNG DẪN TRÌNH BIÊN DỊCH C++
:: ==========================================
set COMPILER_PATH=C:\MinGW\bin
set PATH=%COMPILER_PATH%;%PATH%

echo [.] Dang kiem tra moi truong he thong...
g++ --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [X] Loi: Khong tim thay trinh bien dich g++ tai %COMPILER_PATH%
    pause
    exit
)

:: ==========================================
:: BƯỚC 1: TỰ ĐỘNG BIÊN DỊCH FILE C++
:: ==========================================
echo [.] Dang build ma nguon main.cpp sang rpc_discord.exe...
g++ main.cpp -o rpc_discord.exe -DDISCORD_DYNAMIC_LIB -I. discord-rpc.lib

if %ERRORLEVEL% NEQ 0 (
    echo [X] Loi: Vui long kiem tra lai code main.cpp!
    pause
    exit
)
echo [+=] Bien dich Rich Presence C++ thanh cong!
echo --------------------------------------------------

:: ==========================================
:: BƯỚC 2: KIỂM TRA VÀ CÀI ĐẶT THƯ VIỆN PYTHON
:: ==========================================
echo [.] Dang kiem tra va tu dong cai dat thu vien discord.py...
:: Lenh nay se tu dong bo qua neu may ban da tai san, rat an toan
python -m pip install discord.py >nul 2>&1

:: ==========================================
:: BƯỚC 3: KHỞI CHẠY ĐỒNG THỜI BOT PYTHON VÀ RPC
:: ==========================================
echo [*] Dang khoi dong Bot Tu (Chay cua so rieng)...
:: Giữ lại lệnh cmd /k để nếu có lỗi Token bạn vẫn có thể nhìn thấy log nhé
start "Discord Bot Online" cmd /k python bot.py

echo [*] Dang khoi dong Rich Presence C++...
echo [!] He thong da hoat dong. Giu cua so nay de duy tri sanh cho!
echo --------------------------------------------------

:: Chạy luôn file rpc_discord.exe ngay tại cửa sổ hiện tại
rpc_discord.exe

pause