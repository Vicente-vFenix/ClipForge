"""
Script de diagnóstico para VLC
Ejecutar: python diagnostico_vlc.py
"""

import sys
import os
from pathlib import Path

print("=" * 60)
print("DIAGNÓSTICO VLC - Auto Video Editor Pro")
print("=" * 60)

# 1. Verificar Python
print(f"\n✓ Python: {sys.version}")
print(f"✓ Plataforma: {sys.platform}")
print(f"✓ Arquitectura: {sys.maxsize > 2**32 and '64-bit' or '32-bit'}")

# 2. Verificar módulo python-vlc
print("\n--- Módulo python-vlc ---")
try:
    import vlc
    print(f"✓ python-vlc instalado")
    try:
        version = vlc.libvlc_get_version().decode('utf-8')
        print(f"✓ Versión VLC: {version}")
    except:
        print("⚠ No se pudo obtener versión de VLC")
except ImportError as e:
    print(f"✗ python-vlc NO instalado")
    print(f"\n  SOLUCIÓN: pip install python-vlc")
    sys.exit(1)

# 3. Verificar DLLs de VLC
print("\n--- Archivos VLC ---")
vlc_path = Path(__file__).parent

required_files = {
    'libvlc.dll': 'Core VLC',
    'libvlccore.dll': 'VLC Core Library',
}

all_found = True
for file, desc in required_files.items():
    file_path = vlc_path / file
    if file_path.exists():
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"✓ {file} ({desc}) - {size_mb:.1f} MB")
    else:
        print(f"✗ {file} NO ENCONTRADO")
        all_found = False

# 4. Verificar carpeta plugins
plugins_dir = vlc_path / 'plugins'
if plugins_dir.exists():
    plugin_count = len(list(plugins_dir.rglob('*.dll')))
    print(f"✓ plugins/ - {plugin_count} archivos")
else:
    print(f"✗ plugins/ NO ENCONTRADA")
    all_found = False

# 5. Test de creación de instancia
print("\n--- Test de Inicialización ---")
if all_found:
    try:
        # Configurar paths
        os.environ['PYTHON_VLC_MODULE_PATH'] = str(vlc_path)
        if sys.platform == 'win32':
            try:
                os.add_dll_directory(str(vlc_path))
            except:
                pass
        
        # Intentar crear instancia
        instance = vlc.Instance('--quiet')
        if instance is None:
            print("✗ No se pudo crear instancia VLC (retornó None)")
        else:
            print("✓ Instancia VLC creada correctamente")
            
            # Intentar crear player
            player = instance.media_player_new()
            if player is None:
                print("✗ No se pudo crear media player (retornó None)")
            else:
                print("✓ Media Player creado correctamente")
                
                # Limpiar
                player.release()
                instance.release()
                print("✓ Recursos liberados correctamente")
                
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠ Saltando test - archivos faltantes")

# 6. Resumen
print("\n" + "=" * 60)
if all_found:
    print("✅ DIAGNÓSTICO COMPLETO - Todo OK")
    print("\nPuedes ejecutar la aplicación:")
    print("  python main.py")
else:
    print("❌ FALTAN ARCHIVOS VLC")
    print("\nSOLUCIONES:")
    print("\n1. Descargar VLC 3.0.21 (64-bit):")
    print("   https://get.videolan.org/vlc/3.0.21/win64/vlc-3.0.21-win64.zip")
    print("\n2. Extraer estos archivos a la carpeta del proyecto:")
    print("   - libvlc.dll")
    print("   - libvlccore.dll")
    print("   - plugins/ (carpeta completa)")
    print("\n3. Volver a ejecutar: python diagnostico_vlc.py")

print("=" * 60)
