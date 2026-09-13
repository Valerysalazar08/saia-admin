@echo off
cd /d "%~dp0"
echo ================================================
echo   SAIA Admin - Instalando dependencias
echo ================================================
echo.
python -m pip install --upgrade pip
REM Solo acepta paquetes precompilados: evita que pip intente compilar C/C++.
python -m pip install --only-binary=:all: -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] No se pudieron instalar las dependencias.
    echo Verifica que Python este instalado y agregado al PATH.
    pause
    exit /b 1
)
echo.
echo ================================================
echo   Listo. Ejecuta ejecutar.bat para abrir SAIA.
echo ================================================
pause
