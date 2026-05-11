@echo off
echo ========================================
echo    TubeGet - Build Portable EXE
echo ========================================
echo.

echo [1/4] Instalando dependencias...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERROR: Fallo al instalar dependencias.
    pause
    exit /b 1
)

echo [2/4] Preparando FFmpeg...
python -c "import imageio_ffmpeg,shutil,os; src=imageio_ffmpeg.get_ffmpeg_exe(); os.makedirs('ffmpeg',exist_ok=True); shutil.copy2(src,'ffmpeg\\ffmpeg.exe'); print('OK')"
if %errorlevel% neq 0 (
    echo ERROR: No se pudo copiar FFmpeg.
    pause
    exit /b 1
)

echo [3/4] Limpiando builds anteriores...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist
if exist *.spec del /q *.spec

echo [4/4] Generando EXE portable...
python -m PyInstaller --onefile --windowed --name "TubeGet" ^
    --add-binary "ffmpeg\\ffmpeg.exe;ffmpeg" ^
    --hidden-import customtkinter ^
    --hidden-import yt_dlp ^
    main.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo    EXE generado en: dist\TubeGet.exe
    echo ========================================
) else (
    echo ERROR: Fallo al generar el EXE.
)

pause
