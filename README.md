# ClipForge

> Editor de vídeo automático que detecta las pausas y silencios de tus grabaciones y los recorta, dejándote un vídeo más corto y ágil. Ideal para gameplays, tutoriales y grabaciones largas.
>
> *Automatic video editor that detects pauses and silences in your recordings and cuts them out, leaving you with a shorter, snappier video. Ideal for gameplays, tutorials and long recordings.*

---

## 🇪🇸 Español

### ¿Qué hace?

ClipForge analiza el audio de tu vídeo, detecta dónde hay voz y dónde hay silencio, y genera automáticamente un vídeo recortado conservando solo las partes con voz. Tiene dos modos de detección:

- **Detección por IA (recomendada):** usa un modelo de detección de voz (Silero VAD) que distingue la voz humana del ruido de fondo (clics de ratón, teclado, ventiladores...). Más preciso.
- **Detección por umbral de audio:** método clásico basado en el nivel de volumen en decibelios. Más rápido y sencillo.

### Características

- Recorte automático de silencios conservando solo las partes habladas.
- Aceleración por GPU NVIDIA (NVENC) para exportar mucho más rápido. Si no hay GPU compatible, usa la CPU automáticamente.
- Codificación HEVC (H.265) en tarjetas compatibles para mejor compresión.
- Conserva **todos los canales de audio** del vídeo (por ejemplo, audio del juego + micrófono por separado).
- Exportación en paralelo por bloques para aprovechar la GPU.
- Vista previa del vídeo integrada.
- Línea de tiempo visual con los segmentos detectados.

### Requisitos

- **Windows** (64 bits).
- **Python 3.12** — Importante: NO uses Python 3.13 o superior, porque PyTorch (necesario para la detección por IA) todavía no es compatible. Puedes descargar Python 3.12 desde [aquí](https://www.python.org/downloads/release/python-3120/).
- **FFmpeg** (no incluido — ver instalación).
- **VLC** (no incluido — ver instalación).
- Para la detección por IA: se recomienda una GPU NVIDIA, aunque también funciona en CPU (más lento).

### Instalación

El proyecto incluye un instalador que comprueba tu sistema e instala automáticamente las librerías de Python necesarias.

**Paso 1.** Descarga este repositorio (botón verde **Code → Download ZIP**) y descomprímelo en una carpeta.

**Paso 2.** Consigue **FFmpeg**:
1. Entra en https://www.gyan.dev/ffmpeg/builds/
2. Descarga el paquete *release essentials* (`.zip`).
3. Dentro del zip, en la carpeta `bin`, encontrarás `ffmpeg.exe`, `ffprobe.exe` y `ffplay.exe`.
4. Copia esos tres archivos a la carpeta del proyecto (junto a `main.py`).

**Paso 3.** Consigue **VLC** (versión portable de 64 bits):
1. Entra en https://www.videolan.org/vlc/download-windows.html
2. Descarga la versión **portable** `.zip` de 64 bits (no el instalador).
3. Descomprime el zip y copia a la carpeta del proyecto: `libvlc.dll`, `libvlccore.dll` y la carpeta `plugins` completa.

**Paso 4.** Ejecuta el instalador. Abre una terminal en la carpeta del proyecto y escribe:
```
py -3.12 instalar.py
```
El instalador comprobará tu versión de Python, verificará que FFmpeg y VLC están presentes, e instalará las librerías de Python necesarias (`torch`, `torchaudio`, `numpy`, `python-vlc`). Sigue las indicaciones que te muestre.

### Cómo usarlo

Cuando el instalador diga que todo está listo, arranca el programa con:
```
py -3.12 main.py
```
O haz doble clic en `AutoVideoEditor.bat`.

Después: carga tu vídeo, elige el modo de detección (activa la casilla de IA si quieres usar Silero VAD), pulsa para analizar, revisa los segmentos detectados en la línea de tiempo y exporta. El vídeo resultante se guarda junto al original con el sufijo `_editado`.

### ⚠️ Problemas conocidos

- **Cancelar una exportación y empezar otra enseguida puede fallar.** Si cancelas una exportación en curso, el proceso tarda un poco en detenerse por completo. Si inicias una segunda exportación del **mismo vídeo** antes de que la primera termine de cancelarse, los archivos temporales de ambas pueden entrar en conflicto y la exportación fallará con un error de "unir bloques". **Solución temporal:** espera a que una exportación termine (o se cancele por completo) antes de iniciar otra. Se corregirá en una versión futura.

---

## 🇬🇧 English

### What it does

ClipForge analyzes your video's audio, detects where there is speech and where there is silence, and automatically produces a trimmed video keeping only the spoken parts. It has two detection modes:

- **AI detection (recommended):** uses a voice activity detection model (Silero VAD) that tells human speech apart from background noise (mouse clicks, keyboard, fans...). More accurate.
- **Audio threshold detection:** classic method based on the volume level in decibels. Faster and simpler.

### Features

- Automatic silence trimming, keeping only the spoken parts.
- NVIDIA GPU acceleration (NVENC) for much faster exports. Falls back to CPU automatically if no compatible GPU is found.
- HEVC (H.265) encoding on supported cards for better compression.
- Preserves **all audio channels** of the video (e.g. game audio + microphone separately).
- Parallel chunk-based export to make the most of the GPU.
- Built-in video preview.
- Visual timeline showing the detected segments.

### Requirements

- **Windows** (64-bit).
- **Python 3.12** — Important: do NOT use Python 3.13 or newer, because PyTorch (needed for AI detection) is not compatible yet. You can download Python 3.12 [here](https://www.python.org/downloads/release/python-3120/).
- **FFmpeg** (not included — see installation).
- **VLC** (not included — see installation).
- For AI detection: an NVIDIA GPU is recommended, although it also works on CPU (slower).

### Installation

The project includes an installer that checks your system and automatically installs the required Python libraries.

**Step 1.** Download this repository (green **Code → Download ZIP** button) and unzip it into a folder.

**Step 2.** Get **FFmpeg**:
1. Go to https://www.gyan.dev/ffmpeg/builds/
2. Download the *release essentials* package (`.zip`).
3. Inside the zip, in the `bin` folder, you'll find `ffmpeg.exe`, `ffprobe.exe` and `ffplay.exe`.
4. Copy those three files into the project folder (next to `main.py`).

**Step 3.** Get **VLC** (64-bit portable version):
1. Go to https://www.videolan.org/vlc/download-windows.html
2. Download the **portable** 64-bit `.zip` version (not the installer).
3. Unzip it and copy into the project folder: `libvlc.dll`, `libvlccore.dll` and the whole `plugins` folder.

**Step 4.** Run the installer. Open a terminal in the project folder and type:
```
py -3.12 instalar.py
```
The installer will check your Python version, verify that FFmpeg and VLC are present, and install the required Python libraries (`torch`, `torchaudio`, `numpy`, `python-vlc`). Follow the on-screen instructions.

### How to use it

When the installer says everything is ready, start the program with:
```
py -3.12 main.py
```
Or double-click `AutoVideoEditor.bat`.

Then: load your video, choose the detection mode (tick the AI checkbox if you want to use Silero VAD), click to analyze, review the detected segments in the timeline, and export. The resulting video is saved next to the original with the `_editado` suffix.

### ⚠️ Known issues

- **Cancelling an export and starting another one right away may fail.** If you cancel an ongoing export, the process takes a moment to stop completely. If you start a second export of the **same video** before the first one has finished cancelling, the temporary files of both can conflict and the export will fail with a "merge blocks" error. **Workaround:** wait for an export to finish (or fully cancel) before starting another one. This will be fixed in a future version.
