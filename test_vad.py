"""
Script de prueba para verificar que el sistema VAD está funcionando correctamente
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_pytorch():
    """Verifica instalación de PyTorch"""
    try:
        import torch
        logger.info(f"✅ PyTorch instalado: {torch.__version__}")
        logger.info(f"   CUDA disponible: {torch.cuda.is_available()}")
        return True
    except ImportError:
        logger.error("❌ PyTorch no instalado")
        logger.error("   Ejecuta: pip install torch torchaudio")
        return False

def test_torchaudio():
    """Verifica instalación de torchaudio"""
    try:
        import torchaudio
        logger.info(f"✅ Torchaudio instalado: {torchaudio.__version__}")
        return True
    except ImportError:
        logger.error("❌ Torchaudio no instalado")
        logger.error("   Ejecuta: pip install torchaudio")
        return False

def test_vad_module():
    """Verifica que el módulo VAD se importa correctamente"""
    try:
        from vad_detector import VoiceActivityDetector
        logger.info("✅ Módulo VAD importado correctamente")
        return True
    except ImportError as e:
        logger.error(f"❌ Error importando módulo VAD: {e}")
        return False

def test_vad_model():
    """Intenta cargar el modelo Silero VAD"""
    try:
        logger.info("Intentando cargar modelo Silero VAD...")
        from vad_detector import VoiceActivityDetector
        
        vad = VoiceActivityDetector()
        vad.load_model()
        
        logger.info("✅ Modelo VAD cargado correctamente")
        logger.info("   El modelo está listo para usar")
        return True
    except Exception as e:
        logger.error(f"❌ Error cargando modelo VAD: {e}")
        logger.error("   La primera carga puede tardar (descarga ~1.5MB)")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("="*50)
    print("  VERIFICACIÓN DEL SISTEMA VAD")
    print("="*50)
    print()
    
    tests = [
        ("PyTorch", test_pytorch),
        ("Torchaudio", test_torchaudio),
        ("Módulo VAD", test_vad_module),
        ("Modelo Silero VAD", test_vad_model),
    ]
    
    results = []
    for name, test_func in tests:
        logger.info(f"Probando {name}...")
        result = test_func()
        results.append((name, result))
        print()
    
    print("="*50)
    print("  RESUMEN")
    print("="*50)
    
    all_passed = all(result for _, result in results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    
    if all_passed:
        print("🎉 ¡TODO FUNCIONA CORRECTAMENTE!")
        print("   El sistema VAD está listo para usar.")
        return 0
    else:
        print("⚠️  ALGUNAS PRUEBAS FALLARON")
        print("   Revisa los errores arriba y corrige los problemas.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
