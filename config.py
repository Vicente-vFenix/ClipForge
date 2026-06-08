import sys
import subprocess
import logging
from pathlib import Path

# Logging configuration — StreamHandler con UTF-8 para Windows (cp1252 no soporta emojis)
import io
_stream_handler = logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'buffer') else sys.stdout)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_editor.log', encoding='utf-8'),
        _stream_handler
    ]
)

# Platform-specific subprocess flags
if sys.platform == 'win32':
    subprocess.CREATE_NO_WINDOW = 0x08000000
else:
    subprocess.CREATE_NO_WINDOW = 0

# Application path detection (PyInstaller compatible)
if getattr(sys, 'frozen', False):
    application_path = Path(sys._MEIPASS)
else:
    application_path = Path(__file__).parent

# FFmpeg paths
FFMPEG_PATH = str(application_path / 'ffmpeg.exe')
FFPROBE_PATH = str(application_path / 'ffprobe.exe')

# GPU Detection
def detect_gpu_support():
    """Detect if NVIDIA GPU with NVENC is available"""
    try:
        result = subprocess.run(
            [FFMPEG_PATH, '-hide_banner', '-encoders'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            creationflags=subprocess.CREATE_NO_WINDOW,
            timeout=5
        )
        
        has_nvenc = 'h264_nvenc' in result.stdout
        has_hevc = 'hevc_nvenc' in result.stdout
        
        if has_nvenc or has_hevc:
            # Verify CUDA acceleration
            result_cuda = subprocess.run(
                [FFMPEG_PATH, '-hide_banner', '-hwaccels'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=5
            )
            has_cuda = 'cuda' in result_cuda.stdout
            
            if has_cuda:
                gpu_info = "NVIDIA GPU con NVENC"
                if has_hevc:
                    gpu_info += " (HEVC)"
                logging.info(f"✅ {gpu_info} detectada")
                return True, has_hevc
        
        logging.warning("⚠️ GPU NVIDIA no detectada, usando CPU")
        return False, False
        
    except Exception as e:
        logging.error(f"Error detectando GPU: {e}")
        return False, False

GPU_AVAILABLE, HEVC_AVAILABLE = detect_gpu_support()

# Encoder settings based on GPU availability
# HEVC (H.265) es mejor para RTX 4070: 30-50% mejor compresión que H.264
if GPU_AVAILABLE:
    if HEVC_AVAILABLE:
        VIDEO_ENCODER = 'hevc_nvenc'  # RTX 4070 tiene encoder HEVC muy rápido
        logging.info("🚀 Modo GPU con HEVC activado (mejor calidad)")
    else:
        VIDEO_ENCODER = 'h264_nvenc'
        logging.info("🚀 Modo GPU con H.264 activado")
    
    HWACCEL_FLAGS = ['-hwaccel', 'cuda', '-hwaccel_output_format', 'cuda']
else:
    VIDEO_ENCODER = 'libx264'
    HWACCEL_FLAGS = []
    logging.info("💻 Modo CPU activado")

# Cache directory for temporary files
CACHE_DIR = application_path / 'cache'
CACHE_DIR.mkdir(exist_ok=True)

# Default settings
# RTX 4070 puede manejar p1 (rápido) sin problemas de calidad
DEFAULT_SETTINGS = {
    'umbral': -30,
    'duracion_min': 1.5,  # Optimizado para VAD
    'margen': 0.3,        # Optimizado para VAD
    'preset': 'p1' if GPU_AVAILABLE else 'medium',  # p1 = máxima velocidad en GPU
    'cq': 20  # CQ 20 = excelente calidad (tu GPU lo maneja sin esfuerzo)
}
