"""
Script para compilar Auto Video Editor Pro con PyInstaller
Ejecutar: python build.py
"""

import PyInstaller.__main__
import shutil
from pathlib import Path

def build():
    """Compila la aplicación en un ejecutable standalone"""
    
    print("🚀 Compilando Auto Video Editor Pro...")
    print("=" * 60)
    
    # Rutas
    project_dir = Path(__file__).parent
    dist_dir = project_dir / 'dist' / 'AutoVideoEditor'
    
    # Archivos adicionales a incluir
    add_data = [
        # VLC
        ('libvlc.dll', '.'),
        ('libvlccore.dll', '.'),
        ('plugins', 'plugins'),
        
        # FFmpeg
        ('ffmpeg.exe', '.'),
        ('ffprobe.exe', '.'),
    ]
    
    # Construir argumentos para PyInstaller
    pyinstaller_args = [
        'main.py',
        '--name=AutoVideoEditor',
        '--onedir',  # Un directorio con archivos
        '--windowed',  # Sin consola
        '--clean',
        f'--distpath={project_dir / "dist"}',
        f'--workpath={project_dir / "build"}',
        f'--specpath={project_dir}',
    ]
    
    # Añadir archivos adicionales
    for src, dest in add_data:
        if Path(src).exists():
            pyinstaller_args.append(f'--add-data={src};{dest}')
            print(f"✅ Incluyendo: {src} -> {dest}")
        else:
            print(f"⚠️  No encontrado: {src}")
    
    # Opciones adicionales
    pyinstaller_args.extend([
        '--add-binary=libvlc.dll;.',
        '--add-binary=libvlccore.dll;.',
        '--hidden-import=vlc',
        '--collect-all=vlc',
    ])
    
    print("\n📦 Iniciando PyInstaller...")
    print("=" * 60)
    
    # Ejecutar PyInstaller
    try:
        PyInstaller.__main__.run(pyinstaller_args)
        
        print("\n✅ Compilación completada!")
        print("=" * 60)
        print(f"\n📁 Ejecutable creado en: {dist_dir}")
        print(f"\n▶️  Para ejecutar: {dist_dir / 'AutoVideoEditor.exe'}")
        
        # Crear README en dist
        readme_dist = dist_dir / 'README.txt'
        readme_dist.write_text(
            "Auto Video Editor Pro - v2.0\n"
            "================================\n\n"
            "Para ejecutar:\n"
            "1. Doble click en AutoVideoEditor.exe\n\n"
            "Requisitos:\n"
            "- Windows 10/11 (64-bit)\n"
            "- GPU NVIDIA con NVENC (opcional)\n\n"
            "Soporte:\n"
            "- GitHub: https://github.com/tuusuario/AutoVideoEditor\n"
            "- Email: tu@email.com\n"
        )
        
        print(f"\n📝 README creado en: {readme_dist}")
        
    except Exception as e:
        print(f"\n❌ Error durante la compilación: {e}")
        raise

if __name__ == '__main__':
    # Verificar que PyInstaller está instalado
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller no está instalado")
        print("\nInstala con: pip install pyinstaller")
        exit(1)
    
    build()
