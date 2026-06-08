"""
Script para buscar VLC instalado en el sistema y copiar archivos
Ejecutar: python buscar_vlc_sistema.py
"""

import os
import shutil
from pathlib import Path

print("=" * 60)
print("BUSCADOR DE VLC EN EL SISTEMA")
print("=" * 60)

# Rutas comunes donde VLC se instala
possible_paths = [
    Path("C:/Program Files/VideoLAN/VLC"),
    Path("C:/Program Files (x86)/VideoLAN/VLC"),
    Path(os.path.expanduser("~")) / "AppData/Local/Programs/VLC",
    Path("C:/VLC"),
]

print("\n🔍 Buscando VLC instalado en rutas comunes...\n")

vlc_found = None
for path in possible_paths:
    print(f"Verificando: {path}")
    if path.exists():
        libvlc = path / "libvlc.dll"
        plugins = path / "plugins"
        
        if libvlc.exists() and plugins.exists():
            print(f"  ✓ ¡VLC ENCONTRADO!")
            vlc_found = path
            break
        else:
            print(f"  ✗ Carpeta existe pero archivos incompletos")
    else:
        print(f"  ✗ No existe")

if not vlc_found:
    print("\n❌ VLC no encontrado en rutas comunes")
    print("\nOPCIONES:")
    print("\n1. INSTALAR VLC:")
    print("   - Descarga: https://www.videolan.org/vlc/")
    print("   - Instala normalmente")
    print("   - Ejecuta este script de nuevo")
    print("\n2. INSTALACIÓN AUTOMÁTICA:")
    print("   - Ejecuta: python instalar_vlc.py")
    print("   - El script descargará VLC automáticamente")
    print("\n3. INSTALACIÓN MANUAL:")
    print("   - Descarga: https://get.videolan.org/vlc/3.0.21/win64/vlc-3.0.21-win64.zip")
    print("   - Extrae y copia libvlc.dll, libvlccore.dll, plugins/")
    input("\nPresiona Enter para salir...")
    exit(1)

# VLC encontrado, copiar archivos
print(f"\n{'='*60}")
print("COPIANDO ARCHIVOS DE VLC...")
print(f"{'='*60}")

project_dir = Path(__file__).parent

files_to_copy = [
    'libvlc.dll',
    'libvlccore.dll',
]

print(f"\nOrigen: {vlc_found}")
print(f"Destino: {project_dir}\n")

# Copiar DLLs
copied = 0
for filename in files_to_copy:
    src = vlc_found / filename
    dst = project_dir / filename
    
    if src.exists():
        try:
            shutil.copy2(src, dst)
            size_mb = dst.stat().st_size / (1024 * 1024)
            print(f"✓ {filename} copiado ({size_mb:.1f} MB)")
            copied += 1
        except Exception as e:
            print(f"✗ Error copiando {filename}: {e}")
    else:
        print(f"✗ {filename} no encontrado en origen")

# Copiar plugins
plugins_src = vlc_found / 'plugins'
plugins_dst = project_dir / 'plugins'

if plugins_src.exists():
    try:
        # Eliminar plugins antiguos si existen
        if plugins_dst.exists():
            print("\n⚠ Eliminando carpeta plugins antigua...")
            shutil.rmtree(plugins_dst)
        
        print("📦 Copiando carpeta plugins (puede tardar)...")
        shutil.copytree(plugins_src, plugins_dst)
        
        # Contar archivos
        plugin_count = len(list(plugins_dst.rglob('*.dll')))
        print(f"✓ plugins/ copiada ({plugin_count} archivos)")
        copied += 1
    except Exception as e:
        print(f"✗ Error copiando plugins: {e}")
else:
    print("✗ Carpeta plugins no encontrada en origen")

# Resultado
print(f"\n{'='*60}")
if copied >= 3:
    print("✅ ARCHIVOS COPIADOS EXITOSAMENTE")
    print(f"{'='*60}")
    print("\nArchivos copiados a:")
    print(f"  {project_dir}")
    print("\nVerificación:")
    print(f"  libvlc.dll: {'✓' if (project_dir / 'libvlc.dll').exists() else '✗'}")
    print(f"  libvlccore.dll: {'✓' if (project_dir / 'libvlccore.dll').exists() else '✗'}")
    print(f"  plugins/: {'✓' if (project_dir / 'plugins').exists() else '✗'}")
    print("\nPróximos pasos:")
    print("  1. Ejecuta: python diagnostico_vlc.py")
    print("  2. Si todo está OK, ejecuta: python main.py")
else:
    print("❌ COPIA INCOMPLETA")
    print(f"{'='*60}")
    print("\nNo se pudieron copiar todos los archivos.")
    print("Intenta con el instalador automático:")
    print("  python instalar_vlc.py")

print(f"{'='*60}")
input("\nPresiona Enter para salir...")
