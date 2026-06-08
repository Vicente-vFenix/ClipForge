import tkinter as tk
from tkinter import Canvas
import os
import sys
import logging
import time
from pathlib import Path

# Configurar ruta de VLC ANTES de importar
if getattr(sys, 'frozen', False):
    vlc_path = Path(sys._MEIPASS)
else:
    vlc_path = Path(__file__).parent

# Configurar variables de entorno
os.environ['PYTHON_VLC_MODULE_PATH'] = str(vlc_path)
os.environ['VLC_PLUGIN_PATH'] = str(vlc_path / 'plugins')

# Añadir al PATH
if str(vlc_path) not in os.environ.get('PATH', ''):
    os.environ['PATH'] = str(vlc_path) + os.pathsep + os.environ.get('PATH', '')

# Añadir directorio DLL
if sys.platform == 'win32':
    try:
        os.add_dll_directory(str(vlc_path))
    except:
        pass

import vlc

logger = logging.getLogger(__name__)

class VideoPlayer(tk.Frame):
    """Reproductor VLC integrado con controles completos"""
    
    def __init__(self, parent, video_path, on_time_change=None):
        super().__init__(parent, bg="#1e1e1e")
        
        self.video_path = video_path
        self.on_time_change = on_time_change
        self.is_playing = False
        self.current_time = 0
        self.duration = 0
        self.volume = 50
        self.update_job = None
        
        # VLC instance
        try:
            vlc_args = [
                '--quiet',
                '--no-video-title-show',
                f'--plugin-path={vlc_path / "plugins"}'
            ]
            
            logger.info(f"Inicializando VLC desde: {vlc_path}")
            
            self.instance = vlc.Instance(vlc_args)
            if self.instance is None:
                raise Exception(f"VLC Instance retornó None. Verifica libvlc.dll y plugins/ en {vlc_path}")
            
            self.player = self.instance.media_player_new()
            if self.player is None:
                raise Exception("Media player retornó None")
            
            logger.info("VLC inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando VLC: {e}", exc_info=True)
            raise
        
        self.create_ui()
        self.load_video(video_path)
        self.update_position()
    
    def create_ui(self):
        """Crea la interfaz del reproductor"""
        # Video frame
        self.video_frame = tk.Frame(self, bg="#000000")
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Controls
        controls = tk.Frame(self, bg="#2d2d2d", height=80)
        controls.pack(fill=tk.X, padx=5, pady=(0, 5))
        controls.pack_propagate(False)
        
        # Timeline
        timeline_frame = tk.Frame(controls, bg="#2d2d2d")
        timeline_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
        
        self.timeline = Canvas(timeline_frame, bg="#1e1e1e", height=6, 
                              highlightthickness=0, cursor="hand2")
        self.timeline.pack(fill=tk.X)
        self.timeline.bind("<Button-1>", self.on_timeline_click)
        
        # Time labels
        time_frame = tk.Frame(controls, bg="#2d2d2d")
        time_frame.pack(fill=tk.X, padx=10)
        
        self.time_label = tk.Label(time_frame, text="00:00", bg="#2d2d2d", 
                                   fg="#ffffff", font=('Segoe UI', 9))
        self.time_label.pack(side=tk.LEFT)
        
        self.duration_label = tk.Label(time_frame, text="00:00", bg="#2d2d2d", 
                                       fg="#aaaaaa", font=('Segoe UI', 9))
        self.duration_label.pack(side=tk.RIGHT)
        
        # Buttons
        btn_frame = tk.Frame(controls, bg="#2d2d2d")
        btn_frame.pack(pady=5)
        
        self.btn_rw = tk.Button(btn_frame, text="⏪", command=self.rewind,
                               bg="#555", fg="white", font=('Segoe UI', 12),
                               padx=8, pady=2, relief=tk.FLAT, cursor="hand2")
        self.btn_rw.pack(side=tk.LEFT, padx=2)
        
        self.btn_play = tk.Button(btn_frame, text="▶️", command=self.toggle_play,
                                 bg="#0078d4", fg="white", font=('Segoe UI', 14),
                                 padx=15, pady=2, relief=tk.FLAT, cursor="hand2")
        self.btn_play.pack(side=tk.LEFT, padx=5)
        
        self.btn_ff = tk.Button(btn_frame, text="⏩", command=self.forward,
                               bg="#555", fg="white", font=('Segoe UI', 12),
                               padx=8, pady=2, relief=tk.FLAT, cursor="hand2")
        self.btn_ff.pack(side=tk.LEFT, padx=2)
        
        # Volume
        vol_frame = tk.Frame(btn_frame, bg="#2d2d2d")
        vol_frame.pack(side=tk.LEFT, padx=(15, 0))
        
        tk.Label(vol_frame, text="🔊", bg="#2d2d2d", fg="white", 
                font=('Segoe UI', 10)).pack(side=tk.LEFT)
        
        self.vol_scale = tk.Scale(vol_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                 bg="#2d2d2d", fg="white", highlightthickness=0,
                                 command=self.set_volume, showvalue=0, length=100,
                                 troughcolor="#1e1e1e", activebackground="#0078d4",
                                 cursor="hand2")
        self.vol_scale.set(self.volume)
        self.vol_scale.pack(side=tk.LEFT, padx=5)
    
    def load_video(self, video_path):
        """Carga el video"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video no existe: {video_path}")
        
        logger.info(f"Cargando video: {video_path}")
        
        try:
            media = self.instance.media_new(video_path)
            
            # Configurar para reproducir TODOS los canales de audio mezclados
            media.add_option(':audio-track=0')  # Track principal
            media.add_option(':sout-all')  # Incluir todos los streams
            
            self.player.set_media(media)
            
            if os.name == 'nt':
                self.video_frame.update()
                self.player.set_hwnd(self.video_frame.winfo_id())
            
            # Parsear para obtener duración
            media.parse()
            time.sleep(0.3)
            
            duration_ms = media.get_duration()
            if duration_ms > 0:
                self.duration = duration_ms / 1000.0
            else:
                # Fallback
                self.player.play()
                time.sleep(0.5)
                self.duration = self.player.get_length() / 1000.0
                self.player.stop()
            
            self.update_duration_label()
            self.player.audio_set_volume(self.volume)
            logger.info(f"Video cargado: {self.duration:.1f}s")
            
        except Exception as e:
            logger.error(f"Error cargando video: {e}", exc_info=True)
            raise Exception(f"No se pudo cargar el video:\n{str(e)}")
    
    def toggle_play(self):
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    def play(self):
        self.player.play()
        self.is_playing = True
        self.btn_play.config(text="⏸️")
    
    def pause(self):
        self.player.pause()
        self.is_playing = False
        self.btn_play.config(text="▶️")
    
    def stop(self):
        self.player.stop()
        self.is_playing = False
        self.btn_play.config(text="▶️")
    
    def seek(self, time_seconds):
        if self.duration > 0:
            position = max(0.0, min(time_seconds / self.duration, 1.0))
            self.player.set_position(position)
            self.current_time = time_seconds
            self.update_time_label()
    
    def rewind(self):
        new_time = max(0, self.current_time - 5)
        self.seek(new_time)
    
    def forward(self):
        new_time = min(self.duration, self.current_time + 5)
        self.seek(new_time)
    
    def set_volume(self, val):
        self.volume = int(val)
        self.player.audio_set_volume(self.volume)
    
    def on_timeline_click(self, event):
        """Maneja clicks en la timeline"""
        if self.duration > 0:
            w = self.timeline.winfo_width()
            if w > 0:
                click_pos = max(0, min(event.x / w, 1.0))
                new_time = click_pos * self.duration
                self.seek(new_time)
    
    def update_position(self):
        """Actualiza posición del video"""
        try:
            if self.player.is_playing():
                pos = self.player.get_position()
                if pos >= 0:
                    self.current_time = pos * self.duration
                    self.update_time_label()
                    self.update_timeline()
                    if self.on_time_change:
                        self.on_time_change(self.current_time)
            
            self.update_job = self.after(100, self.update_position)
        except:
            self.update_job = self.after(500, self.update_position)
    
    def update_time_label(self):
        minutes = int(self.current_time // 60)
        seconds = int(self.current_time % 60)
        self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")
    
    def update_duration_label(self):
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        self.duration_label.config(text=f"{minutes:02d}:{seconds:02d}")
    
    def update_timeline(self):
        self.timeline.delete("progress")
        if self.duration > 0:
            w = self.timeline.winfo_width()
            h = self.timeline.winfo_height()
            progress_w = (self.current_time / self.duration) * w
            self.timeline.create_rectangle(0, 0, progress_w, h, 
                                          fill="#0078d4", outline="", 
                                          tags="progress")
    
    def cleanup(self):
        """Limpia recursos"""
        if self.update_job:
            self.after_cancel(self.update_job)
        try:
            self.stop()
            self.player.release()
            self.instance.release()
        except:
            pass
