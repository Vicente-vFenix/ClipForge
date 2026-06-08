"""
Script de instalación automática de VLC para Auto Video Editor Pro
Ejecutar: python instalar_vlc.py
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path

print("=" * 60)
print("INSTALADOR AUTOMÁTICO VLC")
print("Auto Video Editor Pro")
print("=" * 60)

# Configuración
VLC_VERSION = "3.0.21"
VLC_URL = f"https://get.videolan.org/vlc/{VLC_VERSION}/win64/vlc-{VLC_VERSION}-win64.zip"
TEMP_ZIP = "vlc_temp.zip"
TEMP_EXTRACT = "vlc_temp_extract"

project_dir = Path(__file__).parent

print(f"\n📁 Directorio del proyecto: {project_dir}")
print(f"🌐 URL de descarga: {VLC_URL}")

# Paso 1: Descargar VLC
print(f"\n{'='*60}")
print("PASO 1: Descargando VLC 3.0.21 (puede tardar unos minutos)...")
print(f"{'='*60}")

try:
    def download_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(100, (downloaded / total_size) * 100)
        bar_length = 40
        filled = int(bar_length * percent / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f'\r[{bar}] {percent:.1f}% ({downloaded / (1024*1024):.1f} MB)', end='')
    
    urllib.request.urlretrieve(VLC_URL, TEMP_ZIP, download_progress)
    print("\n✓ Descarga completada")
    
except Exception as e:
    print(f"\n✗ Error descargando: {e}")
    print("\n❌ SOLUCIÓN MANUAL:")
    print(f"1. Descarga manualmente desde: {VLC_URL}")
    print(f"2. Guarda el archivo como: {project_dir / TEMP_ZIP}")
    print(f"3. Ejecuta este script de nuevo")
    sys.exit(1)

# Paso 2: Extraer archivos
print(f"\n{'='*60}")
print("PASO 2: Extrayendo archivos...")
print(f"{'='*60}")

try:
    with zipfile.ZipFile(TEMP_ZIP, 'r') as zip_ref:
        zip_ref.extractall(TEMP_EXTRACT)
    print("✓ Archivos extraídos")
except Exception as e:
    print(f"✗ Error extrayendo: {e}")
    sys.exit(1)

# Paso 3: Copiar archivos necesarios
print(f"\n{'='*60}")
print("PASO 3: Copiando archivos necesarios...")
print(f"{'='*60}")

# Buscar la carpeta vlc dentro de la extracción
vlc_extracted = Path(TEMP_EXTRACT) / f"vlc-{VLC_VERSION}"

if not vlc_extracted.exists():
    # Buscar de forma dinámica
    for item in Path(TEMP_EXTRACT).iterdir():
        if item.is_dir() and 'vlc' in item.name.lower():
            vlc_extracted = item
            break

print(f"📂 Carpeta VLC encontrada: {vlc_extracted}")

# Archivos a copiar
files_to_copy = [
    ('libvlc.dll', 'DLL principal de VLC'),
    ('libvlccore.dll', 'DLL core de VLC'),
]

copied_files = 0
for filename, description in files_to_copy:
    src = vlc_extracted / filename
    dst = project_dir / filename
    
    if src.exists():
        shutil.copy2(src, dst)
        size_mb = dst.stat().st_size / (1024 * 1024)
        print(f"✓ {filename} ({description}) - {size_mb:.1f} MB")
        copied_files += 1
    else:
        print(f"✗ {filename} NO ENCONTRADO en {src}")

# Copiar carpeta plugins
plugins_src = vlc_extracted / 'plugins'
plugins_dst = project_dir / 'plugins'

if plugins_src.exists():
    if plugins_dst.exists():
        print("⚠ Eliminando plugins antiguos...")
        shutil.rmtree(plugins_dst)
    
    print("📦 Copiando carpeta plugins (esto puede tardar)...")
    shutil.copytree(plugins_src, plugins_dst)
    
    # Contar archivos
    plugin_count = len(list(plugins_dst.rglob('*.dll')))
    print(f"✓ plugins/ copiada - {plugin_count} archivos")
    copied_files += 1
else:
    print(f"✗ Carpeta plugins NO ENCONTRADA en {plugins_src}")

# Paso 4: Limpiar archivos temporales
print(f"\n{'='*60}")
print("PASO 4: Limpiando archivos temporales...")
print(f"{'='*60}")

try:
    os.remove(TEMP_ZIP)
    print(f"✓ Eliminado: {TEMP_ZIP}")
except:
    pass

try:
    shutil.rmtree(TEMP_EXTRACT)
    print(f"✓ Eliminado: {TEMP_EXTRACT}")
except:
    pass

# Paso 5: Verificar instalación
print(f"\n{'='*60}")
print("PASO 5: Verificando instalación...")
print(f"{'='*60}")

all_ok = True

# Verificar DLLs
for filename, _ in files_to_copy:
    filepath = project_dir / filename
    if filepath.exists():
        print(f"✓ {filename} - OK")
    else:
        print(f"✗ {filename} - FALTA")
        all_ok = False

# Verificar plugins
if plugins_dst.exists():
    print(f"✓ plugins/ - OK")
else:
    print(f"✗ plugins/ - FALTA")
    all_ok = False

# Resultado final
print(f"\n{'='*60}")
if all_ok and copied_files >= 3:
    print("✅ INSTALACIÓN COMPLETADA EXITOSAMENTE")
    print(f"{'='*60}")
    print("\nArchivos instalados en:")
    print(f"  {project_dir}")
    print("\nPróximos pasos:")
    print("  1. Ejecuta: python diagnostico_vlc.py")
    print("  2. Si todo está OK, ejecuta: python main.py")
else:
    print("❌ INSTALACIÓN INCOMPLETA")
    print(f"{'='*60}")
    print("\nAlgunos archivos no se copiaron correctamente.")
    print("Intenta la instalación manual:")
    print(f"\n1. Descarga: {VLC_URL}")
    print("2. Extrae el ZIP")
    print("3. Copia manualmente:")
    print("   - libvlc.dll")
    print("   - libvlccore.dll")
    print("   - plugins/ (carpeta completa)")
    print(f"4. A la carpeta: {project_dir}")

print(f"{'='*60}")
