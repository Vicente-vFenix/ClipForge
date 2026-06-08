import tkinter as tk
import logging
from ui_styles import AppStyles

logger = logging.getLogger(__name__)

class TimelineWidget(tk.Frame):
    """Widget de timeline interactivo con waveform y edición de segmentos"""
    
    def __init__(self, parent, on_segment_change=None, on_seek=None):
        super().__init__(parent, bg=AppStyles.colors['bg_light'])
        
        self.on_segment_change = on_segment_change
        self.on_seek = on_seek
        
        self.segmentos = []
        self.duracion_total = 0
        self.waveform = []
        self.dragging_edge = None
        self.dragging_segment = None
        self.drag_offset = 0
        self.zoom_level = 1.0
        self.scroll_offset = 0
        
        # Cache para renderizado
        self.last_width = 0
        self.last_height = 0
        
        self.create_ui()
    
    def create_ui(self):
        """Crea la interfaz del timeline"""
        # Header
        header = tk.Frame(self, bg=AppStyles.colors['bg_light'])
        header.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            header, text="🎞️ LÍNEA DE TIEMPO", 
            bg=AppStyles.colors['bg_light'],
            fg=AppStyles.colors['text'], 
            font=AppStyles.fonts['heading']
        ).pack(side=tk.LEFT)
        
        self.info_label = tk.Label(
            header, text="", 
            bg=AppStyles.colors['bg_light'],
            fg=AppStyles.colors['text_dim'], 
            font=AppStyles.fonts['body']
        )
        self.info_label.pack(side=tk.RIGHT)
        
        # Canvas con scrollbar
        canvas_container = tk.Frame(self, bg=AppStyles.colors['bg_dark'])
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.canvas = tk.Canvas(
            canvas_container, 
            bg=AppStyles.colors['bg_dark'],
            highlightthickness=0, 
            cursor="crosshair"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bindings
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Configure>", self.on_resize)
        
        # Mouse wheel para zoom
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        
        # Controls
        controls = tk.Frame(self, bg=AppStyles.colors['bg_light'])
        controls.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(
            controls, text="🔍+", 
            command=lambda: self.adjust_zoom(1.3),
            bg=AppStyles.colors['bg_medium'], 
            fg=AppStyles.colors['text'],
            font=AppStyles.fonts['body'], 
            relief=tk.FLAT, 
            padx=12, pady=6,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            controls, text="🔍-", 
            command=lambda: self.adjust_zoom(0.7),
            bg=AppStyles.colors['bg_medium'], 
            fg=AppStyles.colors['text'],
            font=AppStyles.fonts['body'], 
            relief=tk.FLAT, 
            padx=12, pady=6,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            controls, text="🔄 Reset", 
            command=self.reset_view,
            bg=AppStyles.colors['bg_medium'], 
            fg=AppStyles.colors['text'],
            font=AppStyles.fonts['body'], 
            relief=tk.FLAT, 
            padx=12, pady=6,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=2)
        
        # Estadísticas
        self.stats_label = tk.Label(
            controls, text="", 
            bg=AppStyles.colors['bg_light'],
            fg=AppStyles.colors['text_dim'], 
            font=('Segoe UI', 8)
        )
        self.stats_label.pack(side=tk.RIGHT, padx=5)
    
    def set_data(self, segmentos, duracion_total, waveform):
        """Actualiza los datos del timeline"""
        self.segmentos = segmentos
        self.duracion_total = duracion_total
        self.waveform = waveform
        self.update_info()
        self.update_stats()
        self.draw()
        
        logger.info(f"Timeline actualizado: {len(segmentos)} segmentos, {duracion_total:.1f}s")
    
    def update_info(self):
        """Actualiza la información del header"""
        if self.duracion_total > 0:
            h = int(self.duracion_total // 3600)
            m = int((self.duracion_total % 3600) // 60)
            s = int(self.duracion_total % 60)
            
            time_str = f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"
            self.info_label.config(text=f"{len(self.segmentos)} segmentos • {time_str}")
    
    def update_stats(self):
        """Actualiza estadísticas de reducción"""
        if self.segmentos and self.duracion_total > 0:
            tiempo_final = sum(fin - ini for ini, fin in self.segmentos)
            reduccion = ((self.duracion_total - tiempo_final) / self.duracion_total) * 100
            
            self.stats_label.config(
                text=f"Reducción: {reduccion:.1f}% | Duración final: {self.format_time(tiempo_final)}"
            )
    
    def format_time(self, seconds):
        """Formatea segundos a MM:SS"""
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}:{s:02d}"
    
    def adjust_zoom(self, factor):
        """Ajusta el nivel de zoom"""
        old_zoom = self.zoom_level
        self.zoom_level = max(1.0, min(10.0, self.zoom_level * factor))
        
        if old_zoom != self.zoom_level:
            logger.debug(f"Zoom: {self.zoom_level:.2f}x")
            self.draw()
    
    def reset_view(self):
        """Resetea zoom y scroll"""
        self.zoom_level = 1.0
        self.scroll_offset = 0
        self.draw()
    
    def on_mousewheel(self, event):
        """Maneja zoom con rueda del mouse"""
        if event.delta > 0:
            self.adjust_zoom(1.1)
        else:
            self.adjust_zoom(0.9)
    
    def on_resize(self, event):
        """Redibuja cuando cambia el tamaño"""
        new_width = event.width
        new_height = event.height
        
        # Solo redibujar si el cambio es significativo
        if abs(new_width - self.last_width) > 5 or abs(new_height - self.last_height) > 5:
            self.last_width = new_width
            self.last_height = new_height
            self.draw()
    
    def time_from_x(self, x):
        """Convierte coordenada X a tiempo"""
        w = self.canvas.winfo_width()
        if w == 0 or self.duracion_total == 0:
            return 0
        
        # Ajustar por zoom y scroll
        adjusted_x = (x / self.zoom_level) + self.scroll_offset
        return (adjusted_x / w) * self.duracion_total
    
    def x_from_time(self, time):
        """Convierte tiempo a coordenada X"""
        w = self.canvas.winfo_width()
        if w == 0 or self.duracion_total == 0:
            return 0
        
        # Ajustar por zoom y scroll
        x = (time / self.duracion_total) * w
        return (x - self.scroll_offset) * self.zoom_level
    
    def draw(self):
        """Renderiza el timeline completo"""
        self.canvas.delete("all")
        
        if not self.segmentos:
            # Mostrar mensaje si no hay segmentos
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            
            self.canvas.create_text(
                w / 2, h / 2,
                text="Detecta pausas para ver la línea de tiempo",
                fill=AppStyles.colors['text_dim'],
                font=AppStyles.fonts['body']
            )
            return
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w == 0 or h == 0:
            return
        
        cy = h / 2
        
        # Waveform en el fondo
        if self.waveform:
            self.draw_waveform(w, h, cy)
        
        # Segmentos
        self.draw_segments(w, h, cy)
        
        # Grid de tiempo
        self.draw_time_grid(w, h)
    
    def draw_waveform(self, w, h, cy):
        """Dibuja la forma de onda"""
        waveform_samples = len(self.waveform)
        
        for i, amp in enumerate(self.waveform):
            x = w * i / waveform_samples
            x_adjusted = x * self.zoom_level
            
            # Solo dibujar si está visible
            if 0 <= x_adjusted <= w:
                bar_height = amp * h * 0.35
                self.canvas.create_line(
                    x_adjusted, cy - bar_height, 
                    x_adjusted, cy + bar_height,
                    fill=AppStyles.colors['waveform'], 
                    width=1,
                    tags="waveform"
                )
    
    def draw_segments(self, w, h, cy):
        """Dibuja los segmentos de video"""
        for idx, (inicio, fin) in enumerate(self.segmentos):
            x1 = self.x_from_time(inicio)
            x2 = self.x_from_time(fin)
            
            # Solo dibujar si está visible
            if x2 < 0 or x1 > w:
                continue
            
            # Cuerpo del segmento
            self.canvas.create_rectangle(
                x1, 15, x2, h - 15,
                fill=AppStyles.colors['segment'],
                outline=AppStyles.colors['accent'], 
                width=2,
                tags=f"segment_{idx}"
            )
            
            # Handle izquierdo
            self.canvas.create_rectangle(
                x1 - 4, 15, x1 + 4, h - 15,
                fill=AppStyles.colors['accent'], 
                outline="",
                tags=f"handle_left_{idx}"
            )
            
            # Handle derecho
            self.canvas.create_rectangle(
                x2 - 4, 15, x2 + 4, h - 15,
                fill=AppStyles.colors['accent'], 
                outline="",
                tags=f"handle_right_{idx}"
            )
            
            # Número de segmento (si hay espacio)
            if x2 - x1 > 60:
                self.canvas.create_text(
                    (x1 + x2) / 2, cy, 
                    text=f"#{idx + 1}",
                    fill='#000000', 
                    font=AppStyles.fonts['label'],
                    tags=f"label_{idx}"
                )
    
    def draw_time_grid(self, w, h):
        """Dibuja marcas de tiempo"""
        if self.duracion_total == 0:
            return
        
        # Calcular intervalo apropiado
        visible_duration = self.duracion_total / self.zoom_level
        
        if visible_duration < 60:
            interval = 5  # Cada 5 segundos
        elif visible_duration < 600:
            interval = 30  # Cada 30 segundos
        else:
            interval = 60  # Cada minuto
        
        for t in range(0, int(self.duracion_total), interval):
            x = self.x_from_time(t)
            
            if 0 <= x <= w:
                # Línea vertical
                self.canvas.create_line(
                    x, 0, x, 10,
                    fill=AppStyles.colors['text_dim'],
                    width=1
                )
                
                # Etiqueta de tiempo
                self.canvas.create_text(
                    x, 12,
                    text=self.format_time(t),
                    fill=AppStyles.colors['text_dim'],
                    font=('Segoe UI', 7),
                    anchor=tk.N
                )
    
    def draw_playhead(self, time):
        """Dibuja el indicador de reproducción"""
        self.canvas.delete("playhead")
        
        if self.duracion_total > 0:
            x = self.x_from_time(time)
            h = self.canvas.winfo_height()
            
            # Solo dibujar si está visible
            w = self.canvas.winfo_width()
            if 0 <= x <= w:
                self.canvas.create_line(
                    x, 0, x, h, 
                    fill=AppStyles.colors['danger'],
                    width=2, 
                    tags="playhead"
                )
                
                # Círculo en la parte superior
                self.canvas.create_oval(
                    x - 5, 0, x + 5, 10,
                    fill=AppStyles.colors['danger'],
                    outline="",
                    tags="playhead"
                )
    
    def on_click(self, event):
        """Maneja clicks en el canvas"""
        if not self.segmentos:
            return
        
        # Verificar si se hizo click en un handle
        for idx, (inicio, fin) in enumerate(self.segmentos):
            x1, x2 = self.x_from_time(inicio), self.x_from_time(fin)
            
            # Handle izquierdo
            if abs(event.x - x1) < 10:
                self.dragging_edge = 'left'
                self.dragging_segment = idx
                self.drag_offset = event.x - x1
                logger.debug(f"Arrastrando borde izquierdo del segmento {idx}")
                return
            
            # Handle derecho
            if abs(event.x - x2) < 10:
                self.dragging_edge = 'right'
                self.dragging_segment = idx
                self.drag_offset = event.x - x2
                logger.debug(f"Arrastrando borde derecho del segmento {idx}")
                return
        
        # Si no es un handle, hacer seek
        if self.on_seek:
            time = self.time_from_x(event.x)
            self.on_seek(time)
    
    def on_drag(self, event):
        """Maneja arrastre de handles"""
        if self.dragging_edge and self.dragging_segment is not None:
            new_time = max(0, min(
                self.duracion_total, 
                self.time_from_x(event.x - self.drag_offset)
            ))
            
            inicio, fin = self.segmentos[self.dragging_segment]
            
            # Validar límites
            if self.dragging_edge == 'left' and new_time < fin - 0.5:
                self.segmentos[self.dragging_segment] = (new_time, fin)
                self.draw()
                self.update_stats()
                
                if self.on_segment_change:
                    self.on_segment_change(self.segmentos)
            
            elif self.dragging_edge == 'right' and new_time > inicio + 0.5:
                self.segmentos[self.dragging_segment] = (inicio, new_time)
                self.draw()
                self.update_stats()
                
                if self.on_segment_change:
                    self.on_segment_change(self.segmentos)
    
    def on_release(self, event):
        """Maneja liberación del mouse"""
        if self.dragging_edge:
            logger.debug(f"Segmento {self.dragging_segment} ajustado")
        
        self.dragging_edge = None
        self.dragging_segment = None
    
    def on_motion(self, event):
        """Cambia el cursor según la posición"""
        if not self.segmentos:
            return
        
        cursor = "crosshair"
        
        for inicio, fin in self.segmentos:
            x1, x2 = self.x_from_time(inicio), self.x_from_time(fin)
            
            if abs(event.x - x1) < 10 or abs(event.x - x2) < 10:
                cursor = "sb_h_double_arrow"
                break
        
        self.canvas.config(cursor=cursor)
