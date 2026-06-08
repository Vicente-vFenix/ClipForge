@echo off
echo ========================================
echo   Instalando Deteccion de Voz con IA
echo ========================================
echo.

echo [1/3] Instalando PyTorch...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo.
echo [2/3] Verificando instalacion...
python -c "import torch; print(f'PyTorch instalado: {torch.__version__}')"

echo.
echo [3/3] El modelo Silero VAD se descargara automaticamente en el primer uso
echo.

echo ========================================
echo   INSTALACION COMPLETA
echo ========================================
echo.
echo Ya puedes usar la deteccion de voz con IA!
echo El modelo se descargara (~1.5MB) en el primer uso.
echo.
pause
