"""
====================================================================
  INSTALADOR DE ClipForge
====================================================================
  Este script prepara tu equipo para ejecutar ClipForge:

    1. Comprueba que tu version de Python es compatible.
    2. Comprueba que FFmpeg esta presente en la carpeta.
    3. Comprueba que VLC esta presente en la carpeta.
    4. Instala las librerias de Python necesarias (torch, numpy, python-vlc).

  Como usarlo:
    Abre una terminal en esta carpeta y ejecuta:

        py instalar.py

  No borra ni modifica nada de tu sistema. Solo comprueba e instala
  las librerias de Python que faltan.
====================================================================
"""

import sys
import subprocess
from pathlib import Path

# Carpeta donde esta este instalador (la carpeta del programa)
CARPETA = Path(__file__).parent

# Librerias de Python que ClipForge necesita.
# Formato: (nombre para pip, nombre con el que se importa en Python)
DEPENDENCIAS = [
    ("torch", "torch"),
    ("numpy", "numpy"),
    ("python-vlc", "vlc"),
]


def linea():
    print("=" * 64)


def titulo(texto):
    print()
    linea()
    print(f"  {texto}")
    linea()


# --------------------------------------------------------------------
# Paso 1: comprobar la version de Python
# --------------------------------------------------------------------
def comprobar_python():
    titulo("PASO 1 - Comprobando version de Python")

    mayor = sys.version_info.major
    menor = sys.version_info.minor
    print(f"  Python detectado: {mayor}.{menor}")

    if mayor != 3:
        print("  [ERROR] ClipForge necesita Python 3.")
        return False

    # PyTorch (necesario para el detector de voz) no soporta Python 3.13+
    if menor >= 13:
        print()
        print("  [PROBLEMA] Tu version de Python es demasiado nueva.")
        print("  PyTorch (necesario para la deteccion de voz) todavia no")
        print("  es compatible con Python 3.13 o superior.")
        print()
        print("  SOLUCION:")
        print("    1. Instala Python 3.12 desde:")
        print("       https://www.python.org/downloads/release/python-3120/")
        print("    2. Si YA tienes Python 3.12 instalado junto a esta version,")
        print("       vuelve a ejecutar este instalador forzando la 3.12:")
        print("         py -3.12 instalar.py")
        return False

    if menor < 9:
        print()
        print("  [PROBLEMA] Tu version de Python es demasiado antigua.")
        print("  Instala Python 3.12 desde:")
        print("    https://www.python.org/downloads/release/python-3120/")
        return False

    print("  [OK] Version de Python compatible.")
    return True


# --------------------------------------------------------------------
# Paso 2: comprobar FFmpeg
# --------------------------------------------------------------------
def comprobar_ffmpeg():
    titulo("PASO 2 - Comprobando FFmpeg")

    ffmpeg = CARPETA / "ffmpeg.exe"
    ffprobe = CARPETA / "ffprobe.exe"

    falta = []
    if ffmpeg.exists():
        print("  [OK] ffmpeg.exe encontrado.")
    else:
        print("  [FALTA] ffmpeg.exe no esta en la carpeta.")
        falta.append("ffmpeg.exe")

    if ffprobe.exists():
        print("  [OK] ffprobe.exe encontrado.")
    else:
        print("  [FALTA] ffprobe.exe no esta en la carpeta.")
        falta.append("ffprobe.exe")

    if falta:
        print()
        print("  FFmpeg es necesario para analizar y exportar el video.")
        print("  COMO CONSEGUIRLO:")
        print("    1. Entra en: https://www.gyan.dev/ffmpeg/builds/")
        print("    2. Descarga el paquete 'release essentials' (.zip).")
        print("    3. Dentro del zip, en la carpeta 'bin', encontraras:")
        print("         ffmpeg.exe   ffprobe.exe   ffplay.exe")
        print("    4. Copia esos archivos AQUI, junto a este instalador:")
        print(f"         {CARPETA}")
        return False

    return True


# --------------------------------------------------------------------
# Paso 3: comprobar VLC
# --------------------------------------------------------------------
def comprobar_vlc():
    titulo("PASO 3 - Comprobando VLC")

    libvlc = CARPETA / "libvlc.dll"
    libvlccore = CARPETA / "libvlccore.dll"
    plugins = CARPETA / "plugins"

    falta = []
    if libvlc.exists():
        print("  [OK] libvlc.dll encontrado.")
    else:
        print("  [FALTA] libvlc.dll no esta en la carpeta.")
        falta.append("libvlc.dll")

    if libvlccore.exists():
        print("  [OK] libvlccore.dll encontrado.")
    else:
        print("  [FALTA] libvlccore.dll no esta en la carpeta.")
        falta.append("libvlccore.dll")

    if plugins.exists() and plugins.is_dir():
        print("  [OK] carpeta 'plugins' encontrada.")
    else:
        print("  [FALTA] la carpeta 'plugins' no esta.")
        falta.append("plugins/")

    if falta:
        print()
        print("  VLC es necesario para la vista previa del video.")
        print("  COMO CONSEGUIRLO:")
        print("    1. Descarga la version PORTABLE 64-bit de VLC desde:")
        print("       https://www.videolan.org/vlc/download-windows.html")
        print("       (busca el archivo .zip de 64 bits, no el instalador)")
        print("    2. Descomprime el zip.")
        print("    3. De la carpeta de VLC, copia AQUI estos elementos:")
        print("         libvlc.dll")
        print("         libvlccore.dll")
        print("         la carpeta 'plugins' completa")
        print(f"    4. Pegalos junto a este instalador:")
        print(f"         {CARPETA}")
        return False

    return True


# --------------------------------------------------------------------
# Paso 4: instalar las librerias de Python
# --------------------------------------------------------------------
def instalar_dependencias():
    titulo("PASO 4 - Instalando librerias de Python")

    print("  Esto puede tardar varios minutos (PyTorch es grande).")
    print()

    fallidas = []
    for nombre_pip, nombre_import in DEPENDENCIAS:
        # Comprobar si ya esta instalada
        try:
            __import__(nombre_import)
            print(f"  [YA INSTALADO] {nombre_pip}")
            continue
        except ImportError:
            pass

        print(f"  Instalando {nombre_pip} ...")

        # Primer intento: instalacion normal
        resultado = subprocess.run(
            [sys.executable, "-m", "pip", "install", nombre_pip],
            capture_output=True,
            text=True,
        )

        # Algunos sistemas (Python gestionado por el SO) rechazan pip salvo
        # que se use --break-system-packages. Si detectamos ese caso,
        # reintentamos automaticamente con esa opcion.
        if resultado.returncode != 0 and "break-system-packages" in resultado.stderr:
            print("  (reintentando con --break-system-packages)")
            resultado = subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "--break-system-packages", nombre_pip],
                capture_output=True,
                text=True,
            )

        if resultado.returncode == 0:
            print(f"  [OK] {nombre_pip} instalado.")
        else:
            print(f"  [ERROR] No se pudo instalar {nombre_pip}.")
            # Mostrar las ultimas lineas del error para diagnosticar
            error = resultado.stderr.strip().splitlines()
            for linea_error in error[-5:]:
                print(f"        {linea_error}")
            fallidas.append(nombre_pip)

    if fallidas:
        print()
        print(f"  No se pudieron instalar: {', '.join(fallidas)}")
        print("  Revisa tu conexion a internet y vuelve a ejecutar el")
        print("  instalador. Si el error persiste, instala manualmente con:")
        print(f"    py -m pip install {' '.join(fallidas)}")
        return False

    return True


# --------------------------------------------------------------------
# Programa principal
# --------------------------------------------------------------------
def main():
    print()
    linea()
    print("        INSTALADOR DE ClipForge")
    print("        Editor de video automatico")
    linea()

    # Acumulamos el estado de cada comprobacion
    ok_python = comprobar_python()
    if not ok_python:
        # Si Python no sirve, no tiene sentido seguir
        resumen(False, False, False, False)
        return

    ok_ffmpeg = comprobar_ffmpeg()
    ok_vlc = comprobar_vlc()
    ok_deps = instalar_dependencias()

    resumen(ok_python, ok_ffmpeg, ok_vlc, ok_deps)


def resumen(ok_python, ok_ffmpeg, ok_vlc, ok_deps):
    titulo("RESUMEN")

    def marca(valor):
        return "[OK]    " if valor else "[FALTA] "

    print(f"  {marca(ok_python)} Python compatible")
    print(f"  {marca(ok_ffmpeg)} FFmpeg")
    print(f"  {marca(ok_vlc)} VLC")
    print(f"  {marca(ok_deps)} Librerias de Python")
    print()

    if ok_python and ok_ffmpeg and ok_vlc and ok_deps:
        print("  TODO LISTO. Ya puedes ejecutar ClipForge con:")
        print("    py -3.12 main.py")
        print("  o haciendo doble clic en AutoVideoEditor.bat")
    else:
        print("  Aun falta algo (mira los avisos de arriba).")
        print("  Soluciona lo que falte y vuelve a ejecutar:")
        print("    py instalar.py")

    linea()
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print(f"  [ERROR INESPERADO] {e}")
    # Pausa para que la ventana no se cierre de golpe si se ejecuta
    # con doble clic
    input("\n  Pulsa ENTER para salir...")
