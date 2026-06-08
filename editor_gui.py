import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import logging
from pathlib import Path
import subprocess
import os
import wave
import struct

from config import FFMPEG_PATH, FFPROBE_PATH
from video_processor import VideoProcessor
from video_player import VideoPlayer
from ui_styles import AppStyles
from ui_components import ModernButton, Section, LabeledSlider
from timeline_widget import TimelineWidget
from tooltips import add_tooltip

logger = logging.getLogger(__name__)

class EditorVideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Video Editor Pro")
        self.root.geometry("1800x950")
        self.root.minsize(1600, 900)
        self.root.configure(bg=AppStyles.colors['bg_dark'])
        
        self.video_path = tk.StringVar()
        self.umbral = tk.IntVar(value=-30)
        self.duracion = tk.DoubleVar(value=2.0)
        self.margen = tk.DoubleVar(value=0.5)
        self.usar_vad = tk.BooleanVar(value=False)
        self.preset_gpu = tk.StringVar(value="p4")
        self.calidad_cq = tk.IntVar(value=23)
        self.audio_streams = []
        self.audio_stream_selected = tk.IntVar(value=0)
        
        self.processor = VideoProcessor()
        self.segmentos = []
        self.duracion_total = 0
        self.waveform = []
        self.video_loaded = False
        self.video_path_full = ""
        
        self.create_ui()
    
    def create_ui(self):
        top_bar = tk.Frame(self.root, bg=AppStyles.colors['bg_medium'], height=60)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.pack_propagate(False)
        tk.Label(top_bar, text="🎬 Auto Video Editor Pro", bg=AppStyles.colors['bg_medium'],
                fg=AppStyles.colors['accent'], font=AppStyles.fonts['title']).pack(side=tk.LEFT, padx=20)
        
        workspace = tk.Frame(self.root, bg=AppStyles.colors['bg_dark'])
        workspace.pack(fill=tk.BOTH, expand=True)
        
        left_panel = tk.Frame(workspace, bg=AppStyles.colors['bg_medium'], width=900)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)
        
        video_header = tk.Frame(left_panel, bg=AppStyles.colors['bg_medium'], height=40)
        video_header.pack(fill=tk.X)
        tk.Label(video_header, text="📹 VISTA PREVIA", bg=AppStyles.colors['bg_medium'],
                fg=AppStyles.colors['text'], font=AppStyles.fonts['heading']).pack(side=tk.LEFT, padx=15, pady=10)
        
        self.player_container = tk.Frame(left_panel, bg='#000000')
        self.player_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.no_video_label = tk.Label(self.player_container, text="📹\n\nSelecciona un video para comenzar",
                                       bg="#000000", fg="#555555", font=('Segoe UI', 16))
        self.no_video_label.pack(expand=True)
        
        self.timeline = TimelineWidget(left_panel, on_segment_change=self.on_segments_changed, on_seek=self.on_timeline_seek)
        self.timeline.pack(fill=tk.X, padx=10, pady=(0, 10), ipady=100)
        
        right_panel = tk.Frame(workspace, bg=AppStyles.colors['bg_medium'], width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 10), pady=10)
        right_panel.pack_propagate(False)
        
        canvas_scroll = tk.Canvas(right_panel, bg=AppStyles.colors['bg_medium'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=canvas_scroll.yview)
        controls_frame = tk.Frame(canvas_scroll, bg=AppStyles.colors['bg_medium'])
        controls_frame.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_scroll.create_window((0, 0), window=controls_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.build_controls(controls_frame)
    
    def build_controls(self, parent):
        Section(parent, "📁 ARCHIVO DE VIDEO").pack(fill=tk.X, pady=(0, 10))
        ModernButton(parent, "Seleccionar Video", self.select_and_load_video, style='primary').pack(fill=tk.X, padx=15, pady=(0, 10))
        tk.Label(parent, textvariable=self.video_path, bg=AppStyles.colors['bg_medium'],
                fg=AppStyles.colors['text_dim'], font=AppStyles.fonts['body'], wraplength=350).pack(padx=15, pady=(0, 20))
        
        Section(parent, "🎤 CANAL DE AUDIO").pack(fill=tk.X, pady=(0, 10))
        self.audio_channel_frame = tk.Frame(parent, bg=AppStyles.colors['bg_medium'])
        self.audio_channel_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        tk.Label(self.audio_channel_frame, text="Selecciona el canal con tu voz:", bg=AppStyles.colors['bg_medium'],
                fg=AppStyles.colors['text_dim'], font=AppStyles.fonts['body']).pack(anchor=tk.W, pady=(0, 5))
        self.audio_channels_container = tk.Frame(self.audio_channel_frame, bg=AppStyles.colors['bg_medium'])
        self.audio_channels_container.pack(fill=tk.X)
        self.no_audio_label = tk.Label(self.audio_channels_container, text="Carga un video para ver los canales disponibles",
                                        bg=AppStyles.colors['bg_medium'], fg=AppStyles.colors['text_dim'], font=('Segoe UI', 8, 'italic'))
        self.no_audio_label.pack(pady=5)
        
        Section(parent, "🔍 DETECCIÓN DE PAUSAS").pack(fill=tk.X, pady=(0, 10))
        
        sens_slider = LabeledSlider(parent, "Sensibilidad", self.umbral, -45, -15, lambda v: f"{self.umbral.get()} dB")
        sens_slider.pack(fill=tk.X, padx=15, pady=(0, 15))
        add_tooltip(sens_slider, 
                   "💡 Sensibilidad de detección\n\n"
                   "• BAJO (-45dB): MÁS sensible\n"
                   "  Detecta pausas suaves\n\n"
                   "• ALTO (-15dB): MENOS sensible\n"
                   "  Solo pausas muy claras\n\n"
                   "Recomendado: -30dB")
        
        dur_slider = LabeledSlider(parent, "Duración mínima", self.duracion, 0.5, 5.0, 
                                  lambda v: f"{self.duracion.get():.1f}s", resolution=0.1)
        dur_slider.pack(fill=tk.X, padx=15, pady=(0, 15))
        add_tooltip(dur_slider,
                   "💡 Duración mínima de pausa\n\n"
                   "• MENOS (0.5s): Elimina más\n"
                   "  Detecta pausas cortas\n\n"
                   "• MÁS (5.0s): Conserva más\n"
                   "  Solo pausas largas\n\n"
                   "Recomendado: 2.0s")
        
        marg_slider = LabeledSlider(parent, "Margen", self.margen, 0.0, 2.0,
                                   lambda v: f"{self.margen.get():.1f}s", resolution=0.1)
        marg_slider.pack(fill=tk.X, padx=15, pady=(0, 15))
        add_tooltip(marg_slider,
                   "💡 Margen de seguridad\n\n"
                   "Espacio antes/después del corte\n\n"
                   "• SIN margen (0.0s): Preciso\n"
                   "  Puede cortar palabras\n\n"
                   "• CON margen (0.5s): Natural\n"
                   "  Deja respiración\n\n"
                   "Recomendado: 0.5s")
        
        # Detección inteligente con IA
        vad_frame = tk.Frame(parent, bg=AppStyles.colors['bg_medium'])
        vad_frame.pack(fill=tk.X, padx=15, pady=(15, 0))
        
        cb_vad = tk.Checkbutton(
            vad_frame,
            text="🤖 Detección inteligente (IA)",
            variable=self.usar_vad,
            bg=AppStyles.colors['bg_medium'],
            fg=AppStyles.colors['text'],
            selectcolor=AppStyles.colors['bg_dark'],
            activebackground=AppStyles.colors['bg_medium'],
            font=AppStyles.fonts['body'],
            cursor="hand2"
        )
        cb_vad.pack(anchor=tk.W)
        add_tooltip(cb_vad, "Detecta SOLO voz humana con IA\nIgnora automáticamente teclas y ruidos")
        
        
        detect_btn = ModernButton(parent, "🔍 Detectar Pausas", self.detect_segments, style='success')
        detect_btn.pack(fill=tk.X, padx=15, pady=(10, 20))
        add_tooltip(detect_btn, "Analiza el canal seleccionado\ny detecta pausas/silencios")
        
        Section(parent, "⚙️ CALIDAD DE EXPORTACIÓN").pack(fill=tk.X, pady=(0, 10))
        preset_frame = tk.Frame(parent, bg=AppStyles.colors['bg_medium'])
        preset_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        presets_data = [
            ("⚡ Rápido", "p1", "Exportación rápida\nCalidad buena"),
            ("⚖️ Balanceado", "p4", "Equilibrio velocidad/calidad\nRecomendado"),
            ("💎 Calidad", "p7", "Máxima calidad\nMás lento")
        ]
        
        for label, value, tooltip_text in presets_data:
            rb = tk.Radiobutton(preset_frame, text=label, variable=self.preset_gpu, value=value,
                          bg=AppStyles.colors['bg_medium'], fg=AppStyles.colors['text'],
                          selectcolor=AppStyles.colors['bg_dark'], font=AppStyles.fonts['body'],
                          activebackground=AppStyles.colors['bg_medium'], activeforeground=AppStyles.colors['accent'],
                          cursor="hand2")
            rb.pack(anchor=tk.W, pady=2)
            add_tooltip(rb, tooltip_text)
        
        cq_slider = LabeledSlider(parent, "Nivel CQ", self.calidad_cq, 18, 28, lambda v: f"CQ {self.calidad_cq.get()}")
        cq_slider.pack(fill=tk.X, padx=15, pady=(0, 5))
        add_tooltip(cq_slider,
                   "💡 Calidad del video\n\n"
                   "• CQ 18: Excelente calidad\n"
                   "  Archivos más grandes\n\n"
                   "• CQ 23: Óptimo\n"
                   "  Buen equilibrio\n\n"
                   "• CQ 28: Más comprimido\n"
                   "  Archivos más pequeños")
        
        tk.Label(parent, text="18=Excelente • 23=Óptimo • 28=Rápido", bg=AppStyles.colors['bg_medium'],
                fg=AppStyles.colors['text_dim'], font=('Segoe UI', 8)).pack(padx=15, pady=(0, 20))
        
        Section(parent, "🚀 EXPORTACIÓN").pack(fill=tk.X, pady=(0, 10))
        self.process_btn = ModernButton(parent, "🚀 EXPORTAR VIDEO", self.process_video, style='primary')
        self.process_btn.pack(fill=tk.X, padx=15, pady=(0, 10))
        self.stop_btn = ModernButton(parent, "⏹️ DETENER", self.detener, style='danger')
        self.stop_btn.pack(fill=tk.X, padx=15, pady=(0, 10))
        self.stop_btn.config(state=tk.DISABLED)
        
        self.progress = ttk.Progressbar(parent, mode='indeterminate')
        self.status_label = tk.Label(parent, text="", bg=AppStyles.colors['bg_medium'],
                                     fg=AppStyles.colors['text'], font=AppStyles.fonts['body'], wraplength=350)
    
    def select_and_load_video(self):
        f = filedialog.askopenfilename(title="Seleccionar video", filetypes=[("Videos", "*.mp4 *.avi *.mov *.mkv"), ("Todos", "*.*")])
        if f:
            self.video_path_full = f
            self.video_path.set(Path(f).name)
            self.load_video(f)
    
    def load_video(self, path):
        try:
            # Limpiar reproductor anterior de forma segura
            if hasattr(self, 'player'):
                try:
                    self.player.stop()
                    self.player.cleanup()
                    self.player.pack_forget()
                    self.player.destroy()
                    self.root.update()  # Forzar actualización de UI
                except:
                    pass
            
            self.no_video_label.pack_forget()
            
            self.player = VideoPlayer(self.player_container, path, on_time_change=self.on_video_time_change)
            self.player.pack(fill=tk.BOTH, expand=True)
            
            r = subprocess.run([FFPROBE_PATH, '-v', 'error', '-show_entries', 'format=duration',
                               '-of', 'default=noprint_wrappers=1:nokey=1', path],
                              capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.duracion_total = float(r.stdout.strip())
            self.video_loaded = True
            self._waveform_cache = None
            self.detect_audio_channels()
            # Pre-cargar waveform en segundo plano mientras el usuario configura parámetros
            threading.Thread(target=self._preload_waveform, daemon=True).start()
            messagebox.showinfo("✅ Listo", "Video cargado.\n\nSelecciona el canal de audio y haz clic en 'Detectar Pausas'.")
        except Exception as e:
            logger.error(f"Error cargando video: {e}", exc_info=True)
            messagebox.showerror("Error", f"No se pudo cargar el video:\n{str(e)}")
    
    def detect_audio_channels(self):
        try:
            self.audio_streams = self.processor.get_audio_streams(self.video_path_full)
            for widget in self.audio_channels_container.winfo_children():
                widget.destroy()
            if not self.audio_streams:
                tk.Label(self.audio_channels_container, text="No se detectaron canales de audio",
                        bg=AppStyles.colors['bg_medium'], fg=AppStyles.colors['warning'],
                        font=AppStyles.fonts['body']).pack(pady=5)
                return
            for i, stream in enumerate(self.audio_streams):
                desc = f"Canal {i}"
                if stream.get('title') and stream['title'] != f'Audio {i}':
                    desc = stream['title']
                channels = stream.get('channels', '?')
                codec = stream.get('codec', 'unknown')
                detail = f" ({channels}ch, {codec})"
                tk.Radiobutton(self.audio_channels_container, text=desc + detail, variable=self.audio_stream_selected, value=i,
                              bg=AppStyles.colors['bg_medium'], fg=AppStyles.colors['text'],
                              selectcolor=AppStyles.colors['bg_dark'], font=AppStyles.fonts['body'],
                              activebackground=AppStyles.colors['bg_medium'], activeforeground=AppStyles.colors['accent'],
                              cursor="hand2").pack(anchor=tk.W, pady=2)
            logger.info(f"Detectados {len(self.audio_streams)} canales de audio")
        except Exception as e:
            logger.error(f"Error detectando canales de audio: {e}", exc_info=True)
    
    def detect_segments(self):
        if not self.video_loaded or not self.video_path_full:
            messagebox.showerror("Error", "Selecciona un video primero")
            return
        
        # Resetear flag de detener
        self.processor.detener = False
        
        self.status_label.pack(fill=tk.X, padx=15, pady=5)
        self.status_label.config(text=f"🔍 Analizando canal {self.audio_stream_selected.get()}...")
        self.progress.pack(fill=tk.X, padx=15, pady=5)
        self.progress.start(10)
        threading.Thread(target=self._detect_thread, daemon=True).start()
    
    def _detect_thread(self):
        try:
            segs, dur = self.processor.detectar_segmentos(
                self.video_path_full,
                self.umbral.get(),
                self.duracion.get(),
                self.margen.get(),
                audio_stream=self.audio_stream_selected.get(),
                usar_vad=self.usar_vad.get()
            )
            self.segmentos = list(segs)
            self.duracion_total = dur
            selected_stream = self.audio_stream_selected.get()
            cache = self._waveform_cache
            if cache and cache[0] == selected_stream:
                # Waveform ya pre-cargada para este canal
                self.waveform = cache[1]
            else:
                self.root.after(0, lambda: self.status_label.config(text="🎵 Generando forma de onda..."))
                self.waveform = self.extract_waveform(self.video_path_full, stream_idx=selected_stream)
            self.root.after(0, lambda: self.timeline.set_data(self.segmentos, self.duracion_total, self.waveform))
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.pack_forget())
            self.root.after(0, lambda: self.status_label.config(text=f"✅ {len(self.segmentos)} segmentos detectados"))
            self.root.after(0, lambda: messagebox.showinfo("✅ Detección completa",
                                                          f"{len(self.segmentos)} segmentos detectados.\n\nArrastra los bordes blancos para ajustar."))
        except Exception as e:
            logger.error(f"Error en detección: {e}", exc_info=True)
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.pack_forget())
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
    
    def extract_waveform(self, video_path, stream_idx=0):
        try:
            import tempfile
            tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_audio = tmp.name
            tmp.close()
            cmd = [FFMPEG_PATH, '-i', video_path, '-map', f'0:a:{stream_idx}',
                   '-vn', '-acodec', 'pcm_s16le', '-ar', '8000', '-ac', '1', '-y', temp_audio]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            with wave.open(temp_audio, 'rb') as wav:
                n_frames = wav.getnframes()
                audio_data = wav.readframes(n_frames)
                samples = struct.unpack(f'{n_frames}h', audio_data)
                max_val = max(abs(min(samples)), abs(max(samples)))
                normalized = [s / max_val for s in samples] if max_val > 0 else samples
                samples_per_pixel = max(1, len(normalized) // 2000)
                waveform = []
                for i in range(0, len(normalized), samples_per_pixel):
                    chunk = normalized[i:i+samples_per_pixel]
                    if chunk:
                        waveform.append((sum(s**2 for s in chunk) / len(chunk)) ** 0.5)
            try:
                os.remove(temp_audio)
            except Exception:
                pass
            return waveform
        except Exception:
            return []

    def _preload_waveform(self):
        stream = self.audio_stream_selected.get()
        data = self.extract_waveform(self.video_path_full, stream_idx=stream)
        self._waveform_cache = (stream, data)
        logger.info(f"Waveform pre-cargada (canal {stream})")
    
    def on_segments_changed(self, segments):
        self.segmentos = segments
    
    def on_timeline_seek(self, time):
        if hasattr(self, 'player'):
            self.player.seek(time)
    
    def on_video_time_change(self, time):
        self.timeline.draw_playhead(time)
    
    def detener(self):
        self.processor.detener = True
        self.progress.stop()
        self.progress.pack_forget()
        self.process_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="❌ Proceso detenido")
    
    def process_video(self):
        if not self.segmentos:
            messagebox.showerror("Error", "Detecta pausas primero")
            return
        self.processor.detener = False
        self.process_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.pack(fill=tk.X, padx=15, pady=5)
        self.progress.start(10)
        self.status_label.pack(fill=tk.X, padx=15, pady=5)
        self.status_label.config(text="🚀 Exportando...")
        threading.Thread(target=self._process_thread, daemon=True).start()
    
    def _process_thread(self):
        try:
            self.processor.procesar_segmentos(self.video_path_full, self.segmentos, self.preset_gpu.get(), self.calidad_cq.get(),
                                             callback=lambda msg: self.root.after(0, lambda: self.status_label.config(text=msg)))
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.pack_forget())
            self.root.after(0, lambda: self.process_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.status_label.config(text="✅ Exportación completa"))
            self.root.after(0, lambda: messagebox.showinfo("✅ Completado", f"Video exportado:\n{Path(self.video_path_full).stem}_editado.mp4"))
        except Exception as e:
            logger.error(f"Error en exportación: {e}", exc_info=True)
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.pack_forget())
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.process_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
    
    def on_closing(self):
        """Cierra la aplicación limpiamente"""
        if hasattr(self, 'player'):
            try:
                self.player.cleanup()
            except:
                pass
        self.root.destroy()
