import torch
import subprocess
import os
import numpy as np
import logging
from pathlib import Path
from config import FFMPEG_PATH, CACHE_DIR

class SileroVADDetector:
    """
    Detector de voz usando Silero VAD (Voice Activity Detection)
    Ignora automáticamente teclas, clicks y ruidos no-vocales
    Lee audio con FFmpeg (no requiere torchcodec)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.utils = None
        self.sample_rate = 16000
        
    def _cargar_modelo(self):
        """Carga el modelo Silero VAD (solo la primera vez)"""
        if self.model is not None:
            return
        
        try:
            self.logger.info("Cargando modelo Silero VAD...")
            self.model, self.utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            self.logger.info("Modelo Silero VAD cargado")
        except Exception as e:
            raise Exception(
                f"Error cargando Silero VAD: {e}\n\n"
                "Instala PyTorch: pip install torch --break-system-packages"
            )
    
    def detectar_voz(self, video_path, audio_stream=0, margen=0.3, 
                     min_speech_duration=0.3, min_silence_duration=0.5,
                     duracion_total=None, progress_callback=None):
        """Detecta segmentos donde hay VOZ humana"""
        
        # Cargar modelo
        self._cargar_modelo()
        
        if progress_callback:
            progress_callback("Extrayendo audio para VAD...")
        
        # Extraer audio a WAV mono 16kHz con FFmpeg
        temp_audio = CACHE_DIR / "temp_vad_analysis.wav"
        
        cmd = [
            FFMPEG_PATH,
            '-i', video_path,
            '-map', f'0:a:{audio_stream}',
            '-ar', '16000',
            '-ac', '1',
            '-acodec', 'pcm_s16le',
            '-y', str(temp_audio)
        ]
        
        self.logger.info(f"Extrayendo audio del canal {audio_stream}...")
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode != 0:
            raise Exception(f"Error extrayendo audio: {result.stderr}")
        
        if progress_callback:
            progress_callback("Analizando voz con IA...")
        
        # Leer audio con FFmpeg
        try:
            self.logger.info("Leyendo audio con FFmpeg...")
            
            cmd_read = [
                FFMPEG_PATH,
                '-i', str(temp_audio),
                '-f', 's16le',
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-'
            ]
            
            result = subprocess.run(
                cmd_read,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode != 0:
                raise Exception(f"Error leyendo audio: {result.stderr}")
            
            # Convertir bytes a numpy array
            audio_data = np.frombuffer(result.stdout, dtype=np.int16)
            
            # Normalizar a float32 [-1, 1]
            wav = torch.from_numpy(audio_data.astype(np.float32) / 32768.0)
            
            self.logger.info(f"Audio leído: {len(audio_data)} samples ({len(audio_data)/16000:.1f}s)")
            
        except Exception as e:
            raise Exception(f"Error cargando audio: {e}")
        
        # Detectar voz con Silero VAD
        self.logger.info(f"Detectando voz en CPU (umbral: 0.5, min_speech: {int(min_speech_duration*1000)}ms)...")
        
        try:
            (get_speech_timestamps, _, _, _, _) = self.utils
            
            speech_timestamps = get_speech_timestamps(
                wav,
                self.model,
                sampling_rate=self.sample_rate,
                min_speech_duration_ms=int(min_speech_duration * 1000),
                min_silence_duration_ms=int(min_silence_duration * 1000),
                threshold=0.5,
                return_seconds=False
            )
            
            self.logger.info(f"Segmentos de voz detectados: {len(speech_timestamps)}")
            
        except Exception as e:
            raise Exception(f"Error en detección VAD: {e}")
        
        if not speech_timestamps:
            raise Exception("No se detectó voz en el video")
        
        self.logger.info("Convirtiendo timestamps a segundos...")
        
        # Convertir timestamps a segundos y aplicar margen
        segmentos = []
        for ts in speech_timestamps:
            inicio = ts['start'] / self.sample_rate
            fin = ts['end'] / self.sample_rate
            inicio_con_margen = max(0, inicio - margen)
            fin_con_margen = fin + margen
            segmentos.append((inicio_con_margen, fin_con_margen))
        
        self.logger.info(f"Fusionando {len(segmentos)} segmentos...")
        
        # Fusionar segmentos muy cercanos
        segmentos = self._fusionar_segmentos_cercanos(segmentos, gap=0.3)
        
        self.logger.info(f"Segmentos fusionados: {len(segmentos)}")
        
        # Usar duración proporcionada o calcularla si no se pasó
        if duracion_total is None:
            self.logger.info("Obteniendo duración del video...")
            duracion = self._get_duration(video_path)
            self.logger.info(f"Duración obtenida: {duracion:.1f}s")
        else:
            duracion = duracion_total
            self.logger.info(f"Usando duración proporcionada: {duracion:.1f}s")
        
        # Limpiar archivo temporal
        try:
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
        except:
            pass
        
        # Estadísticas
        tiempo_voz = sum(fin - ini for ini, fin in segmentos)
        self.logger.info(f"Tiempo total con voz: {tiempo_voz:.1f}s")
        
        if progress_callback:
            progress_callback(f"{len(segmentos)} segmentos de voz detectados")
        
        self.logger.info("Retornando segmentos...")
        
        return segmentos, duracion
    
    def _fusionar_segmentos_cercanos(self, segmentos, gap=0.3):
        """Fusiona segmentos que están muy cerca uno del otro"""
        if not segmentos:
            return []
        
        fusionados = []
        actual_inicio, actual_fin = segmentos[0]
        
        for inicio, fin in segmentos[1:]:
            if inicio - actual_fin <= gap:
                actual_fin = max(actual_fin, fin)
            else:
                fusionados.append((actual_inicio, actual_fin))
                actual_inicio, actual_fin = inicio, fin
        
        fusionados.append((actual_inicio, actual_fin))
        
        return fusionados
    
    def _get_duration(self, video_path):
        """Extrae la duración del video"""
        cmd = [
            FFMPEG_PATH,
            '-i', video_path,
            '-f', 'null', '-'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        for line in result.stderr.split('\n'):
            if 'Duration:' in line:
                time_str = line.split('Duration:')[1].split(',')[0].strip()
                h, m, s = time_str.split(':')
                return int(h) * 3600 + int(m) * 60 + float(s)
        
        return 0
