import subprocess
import os
import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from config import FFMPEG_PATH, FFPROBE_PATH, GPU_AVAILABLE, VIDEO_ENCODER, HWACCEL_FLAGS, CACHE_DIR

class VideoProcessor:
    def __init__(self):
        self.detener = False
        self.archivos_temp = []
        self.logger = logging.getLogger(__name__)
        self.vad_detector = None  # Se carga bajo demanda
    
    def get_audio_streams(self, vp):
        """Obtiene información de todos los canales de audio del video"""
        if not os.path.exists(vp):
            raise Exception(f"El archivo no existe: {vp}")
        
        try:
            r = subprocess.run(
                [FFPROBE_PATH, '-v', 'quiet', '-print_format', 'json',
                 '-show_streams', '-select_streams', 'a', vp],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=10
            )
            
            data = json.loads(r.stdout)
            streams = data.get('streams', [])
            
            audio_info = []
            for i, stream in enumerate(streams):
                info = {
                    'index': stream.get('index', i),
                    'codec': stream.get('codec_name', 'unknown'),
                    'channels': stream.get('channels', 0),
                    'channel_layout': stream.get('channel_layout', 'unknown'),
                    'sample_rate': stream.get('sample_rate', 'unknown'),
                    'title': stream.get('tags', {}).get('title', f'Audio {i}')
                }
                audio_info.append(info)
            
            self.logger.info(f"Canales de audio encontrados: {len(audio_info)}")
            for i, info in enumerate(audio_info):
                self.logger.info(f"  Canal {i}: {info['title']} - {info['channels']} canales - {info['codec']}")
            
            return audio_info
            
        except Exception as e:
            self.logger.error(f"Error obteniendo streams de audio: {e}")
            return []
    
    def detectar_segmentos(self, vp, umbral, dur_min, margen, progress_callback=None, audio_stream=0, umbral_voz=None, usar_vad=True):
        """Detecta segmentos de audio eliminando pausas
        
        Args:
            vp: ruta del video
            umbral: umbral de ruido en dB (solo si usar_vad=False)
            dur_min: duración mínima de pausa en segundos (solo si usar_vad=False)
            margen: margen adicional antes/después de cortes
            progress_callback: función para actualizar progreso
            audio_stream: índice del canal de audio a analizar
            umbral_voz: umbral mínimo de voz (opcional, para ignorar ruidos bajos)
            usar_vad: Si True, usa detección de voz IA. Si False, usa método antiguo
        """
        
        if not os.path.exists(vp):
            raise Exception(f"El archivo no existe: {vp}")
        
        if self.detener:
            raise Exception("Proceso cancelado")
        
        self.logger.info(f"Iniciando detección en: {vp}")
        self.logger.info(f"Analizando canal de audio: {audio_stream}")
        
        # Obtener duración total
        if progress_callback:
            progress_callback("Obteniendo información del video...")
        
        if self.detener:
            raise Exception("Proceso cancelado")
        
        r = subprocess.run(
            [FFPROBE_PATH, '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'json', vp], 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='ignore',
            creationflags=subprocess.CREATE_NO_WINDOW,
            timeout=30
        )
        
        if not r.stdout or r.stdout.strip() == '':
            raise Exception(f"FFprobe no pudo leer el video.\n\nError: {r.stderr}")
        
        try:
            data = json.loads(r.stdout)
            dur_total = float(data['format']['duration'])
            self.logger.info(f"Duración total: {dur_total:.2f}s")
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise Exception(f"No se pudo obtener la duración: {str(e)}")
        
        if self.detener:
            raise Exception("Proceso detenido por usuario")
        
        # MODO VAD: Detección de voz con IA
        if usar_vad:
            self.logger.info("🎤 Modo VAD activado - Detección inteligente de voz")
            if self.vad_detector is None:
                try:
                    from vad_detector import SileroVADDetector
                    self.vad_detector = SileroVADDetector()
                except ImportError as e:
                    raise Exception(
                        "No se pudo cargar el detector VAD.\n\n"
                        "Instala las dependencias:\n"
                        "pip install torch torchaudio --break-system-packages"
                    )
            
            return self.vad_detector.detectar_voz(
                vp, 
                audio_stream=audio_stream,
                margen=margen,
                min_speech_duration=dur_min,
                duracion_total=dur_total,
                progress_callback=progress_callback
            )
        
        # MODO LEGACY: Detección simple por umbral (antiguo método)
        else:
            self.logger.info("📊 Usando detección simple por umbral de audio")
            
            # Si hay umbral de voz, usar ese umbral
            if umbral_voz is not None:
                self.logger.info(f"Modo umbral de voz activado: usando {umbral_voz}dB en lugar de {umbral}dB")
                umbral = umbral_voz
            
            # Detectar silencios en el canal especificado
            if progress_callback:
                progress_callback(f"Analizando canal {audio_stream} (umbral: {umbral}dB)...")
            
            self.logger.info(f"Parámetros: umbral={umbral}dB, dur_min={dur_min}s, margen={margen}s, canal={audio_stream}")
            
            # Filtro de audio para seleccionar canal específico y detectar silencios
            audio_filter = f'[0:a:{audio_stream}]silencedetect=noise={umbral}dB:d={dur_min}[out]'
            
            r = subprocess.run(
                [FFMPEG_PATH, '-i', vp, 
                 '-filter_complex', audio_filter,
                 '-map', '[out]',
                 '-f', 'null', '-'],
                capture_output=True, 
                text=True, 
                encoding='utf-8', 
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Parsear silencios detectados
            silencios = []
            for line in r.stderr.split('\n'):
                try:
                    if 'silence_start' in line:
                        parts = line.split('silence_start:')
                        if len(parts) > 1:
                            silencios.append({'inicio': float(parts[1].strip().split()[0])})
                    elif 'silence_end' in line and silencios:
                        parts = line.split('silence_end:')
                        if len(parts) > 1 and silencios and 'fin' not in silencios[-1]:
                            silencios[-1]['fin'] = float(parts[1].strip().split('|')[0].strip())
                except (ValueError, IndexError) as e:
                    self.logger.debug(f"Error parseando línea: {line} - {e}")
                    continue
            
            self.logger.info(f"Silencios detectados: {len(silencios)}")
            
            if not silencios:
                raise Exception(
                    f"No se detectaron pausas en el canal {audio_stream}.\n\n"
                    f"Prueba:\n"
                    f"• Reducir sensibilidad (-40 dB)\n"
                    f"• Reducir duración mínima (1.0s)\n"
                    f"• Seleccionar otro canal de audio\n"
                    f"• O activar 'Detección de voz con IA'"
                )
            
            # Crear segmentos de audio útil (entre silencios)
            segs, t = [], 0
            for s in silencios:
                if 'fin' in s:
                    # Aplicar margen para no cortar demasiado cerca
                    inicio_seg = max(0, t - margen)
                    fin_seg = min(s['inicio'] + margen, dur_total)
                    
                    if fin_seg - inicio_seg > 0.3:  # Segmento mínimo de 0.3s
                        segs.append((inicio_seg, fin_seg))
                    t = s['fin']
            
            # Añadir último segmento si queda contenido
            if t < dur_total - 0.5:
                segs.append((max(0, t - margen), dur_total))
            
            if not segs:
                raise Exception("No se pudieron crear segmentos válidos.\n\nEl video podría no tener pausas significativas.")
        
        # Calcular estadísticas
        tiempo_original = dur_total
        tiempo_final = sum(fin - ini for ini, fin in segs)
        reduccion = ((tiempo_original - tiempo_final) / tiempo_original) * 100
        
        self.logger.info(f"Segmentos creados: {len(segs)}")
        self.logger.info(f"Tiempo original: {tiempo_original:.1f}s → Final: {tiempo_final:.1f}s")
        self.logger.info(f"Reducción: {reduccion:.1f}%")
        
        if progress_callback:
            progress_callback(f"✅ {len(segs)} segmentos ({reduccion:.0f}% reducción)")
        
        return segs, dur_total
    
    # =========================================================================
    # ZONA PROTEGIDA — NO MODIFICAR
    # Construye el filter_complex para un chunk manteniendo TODOS los canales
    # de audio del video original. Cualquier cambio aquí rompe el multi-canal.
    # =========================================================================
    def _construir_filtros_chunk(self, chunk_segs, num_audio):
        """Devuelve (filter_complex, audio_outputs) para un chunk de segmentos.

        Preserva todos los canales de audio: por cada canal s se genera una
        cadena atrim independiente y un concat propio, mapeados por separado.
        """
        n = len(chunk_segs)
        video_parts = []
        audio_parts = [[] for _ in range(num_audio)]

        for i, (ini, fin) in enumerate(chunk_segs):
            video_parts.append(
                f"[0:v]trim=start={ini:.6f}:end={fin:.6f},setpts=PTS-STARTPTS[v{i}]"
            )
            for s in range(num_audio):
                audio_parts[s].append(
                    f"[0:a:{s}]atrim=start={ini:.6f}:end={fin:.6f},asetpts=PTS-STARTPTS[a{s}_{i}]"
                )

        all_filters = list(video_parts)
        for ap in audio_parts:
            all_filters.extend(ap)

        video_concat = "".join(f"[v{i}]" for i in range(n))
        all_filters.append(f"{video_concat}concat=n={n}:v=1:a=0[vout]")

        audio_outputs = []
        for s in range(num_audio):
            audio_concat = "".join(f"[a{s}_{i}]" for i in range(n))
            all_filters.append(f"{audio_concat}concat=n={n}:v=0:a=1[a{s}out]")
            audio_outputs.append(f"[a{s}out]")

        return ";".join(all_filters), audio_outputs
    # =========================================================================
    # FIN ZONA PROTEGIDA
    # =========================================================================

    def procesar_segmentos(self, vp, segs, preset, cq, callback=None):
        """Exporta chunks en paralelo (3 simultáneos).

        Los filtros no cambian — solo se ejecutan varios chunks a la vez.
        RTX 4070 soporta hasta 5 sesiones NVENC concurrentes, 3 es seguro.
        La construcción de filtros (multi-canal) está en _construir_filtros_chunk.
        """
        base = os.path.splitext(vp)[0]
        out = f"{base}_editado.mp4"

        total_segs = len(segs)
        self.logger.info(f"Exportando {total_segs} segmentos")

        audio_streams = self.get_audio_streams(vp)
        num_audio = len(audio_streams)
        self.logger.info(f"Video tiene {num_audio} canales de audio")

        CHUNK_SIZE = 50
        MAX_PARALLEL = 3
        chunks = [segs[i:i + CHUNK_SIZE] for i in range(0, total_segs, CHUNK_SIZE)]
        self.logger.info(f"Dividido en {len(chunks)} chunks — {MAX_PARALLEL} en paralelo")

        lista = CACHE_DIR / f"{Path(vp).stem}_chunks.txt"
        chunk_files_map = {}   # chunk_idx → Path
        lock = threading.Lock()
        done_count = [0]

        def encode_chunk(chunk_idx, chunk_segs):
            if self.detener:
                return chunk_idx, None

            chunk_file = CACHE_DIR / f"{Path(vp).stem}_chunk_{chunk_idx}.mp4"

            # Seek 2s before the first segment so ffmpeg doesn't decode from t=0.
            # After -ss, PTS normalizes to 0 at the seek point, so trim times
            # must be relative (subtract seek_to from every timestamp).
            seek_to = max(0, chunk_segs[0][0] - 2.0)
            rel_segs = [(ini - seek_to, fin - seek_to) for ini, fin in chunk_segs]
            filter_complex, audio_outputs = self._construir_filtros_chunk(rel_segs, num_audio)

            cmd = [FFMPEG_PATH]
            if GPU_AVAILABLE:
                cmd.extend(['-hwaccel', 'cuda'])
            if seek_to > 0:
                cmd.extend(['-ss', f'{seek_to:.3f}'])
            cmd.extend(['-i', vp, '-filter_complex', filter_complex, '-map', '[vout]'])
            for ao in audio_outputs:
                cmd.extend(['-map', ao])

            if GPU_AVAILABLE:
                cmd.extend([
                    '-c:v', VIDEO_ENCODER,
                    '-preset', preset,
                    '-tune', 'hq',
                    '-rc', 'vbr',
                    '-cq', str(cq),
                    '-b:v', '0',
                    '-c:a', 'aac',
                    '-b:a', '256k',
                ])
            else:
                cmd.extend([
                    '-c:v', 'libx264',
                    '-preset', preset,
                    '-crf', str(cq),
                    '-c:a', 'aac',
                    '-b:a', '256k',
                ])

            cmd.extend(['-y', str(chunk_file)])

            r = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if r.returncode != 0:
                self.logger.error(f"Error chunk {chunk_idx}: {r.stderr[-500:]}")
                raise Exception(f"Error procesando bloque {chunk_idx + 1}")

            with lock:
                done_count[0] += 1
                if callback:
                    pct = min(95, int(done_count[0] / len(chunks) * 95))
                    callback(f"Exportando... {pct}% ({done_count[0]}/{len(chunks)} bloques)")

            return chunk_idx, chunk_file

        try:
            with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as executor:
                futures = {
                    executor.submit(encode_chunk, idx, chunk_segs): idx
                    for idx, chunk_segs in enumerate(chunks)
                }
                for future in as_completed(futures):
                    if self.detener:
                        raise Exception("Proceso detenido por usuario")
                    chunk_idx, chunk_file = future.result()
                    if chunk_file:
                        chunk_files_map[chunk_idx] = chunk_file

            if self.detener:
                raise Exception("Proceso detenido por usuario")

            # Ordenar por índice para el concat final
            chunk_files = [chunk_files_map[i] for i in range(len(chunks))]

            if callback:
                callback("Uniendo bloques (stream copy)...")

            with open(lista, 'w', encoding='utf-8') as f:
                for cf in chunk_files:
                    f.write(f"file '{cf.resolve()}'\n")

            cmd_final = [
                FFMPEG_PATH,
                '-f', 'concat',
                '-safe', '0',
                '-i', str(lista),
                '-map', '0',
                '-c', 'copy',
                '-movflags', '+faststart',
                '-y', out
            ]

            result = subprocess.run(
                cmd_final,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode != 0:
                self.logger.error(f"Error concat: {result.stderr}")
                raise Exception("Error al unir bloques")

            self.logger.info(f"Video exportado: {out}")
            if callback:
                callback("Exportacion completa")
            return out

        finally:
            for cf in chunk_files_map.values():
                try:
                    if cf.exists():
                        cf.unlink()
                except Exception:
                    pass
            try:
                if lista.exists():
                    lista.unlink()
            except Exception:
                pass
    
    def limpiar_temp(self, lista_path=None):
        """Limpia archivos temporales (no usado en modo filtro complejo)"""
        pass
    
    def get_video_info(self, vp):
        """Obtiene información detallada del video"""
        try:
            r = subprocess.run(
                [FFPROBE_PATH, '-v', 'quiet', '-print_format', 'json',
                 '-show_format', '-show_streams', vp],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=10
            )
            
            return json.loads(r.stdout)
        except Exception as e:
            self.logger.error(f"Error obteniendo info del video: {e}")
            return None
