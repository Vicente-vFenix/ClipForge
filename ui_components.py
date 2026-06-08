import tkinter as tk
from ui_styles import AppStyles

class ToolTip:
    """Tooltip mejorado para mostrar ayuda contextual"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        
        self.widget.bind('<Enter>', self.show_tip)
        self.widget.bind('<Leave>', self.hide_tip)
    
    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            tw, text=self.text, 
            justify=tk.LEFT,
            background=AppStyles.colors['bg_light'], 
            foreground=AppStyles.colors['text'],
            relief=tk.SOLID, 
            borderwidth=1,
            font=AppStyles.fonts['body'],
            padx=8,
            pady=6
        )
        label.pack()
    
    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class ModernButton(tk.Button):
    """Botón moderno con efectos hover y tooltips opcionales"""
    def __init__(self, parent, text, command, style='primary', tooltip=None, **kwargs):
        colors = AppStyles.colors
        
        styles = {
            'primary': (colors['accent'], '#000000', colors['accent_dim']),
            'success': (colors['success'], '#ffffff', '#2d8a3c'),
            'danger': (colors['danger'], '#ffffff', '#d63939'),
            'secondary': (colors['bg_medium'], colors['text'], colors['bg_light'])
        }
        
        bg, fg, hover_bg = styles.get(style, styles['primary'])
        
        super().__init__(
            parent, text=text, command=command,
            bg=bg, fg=fg, font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT, padx=20, pady=10, cursor="hand2",
            activebackground=hover_bg,
            activeforeground=fg,
            **kwargs
        )
        
        # Hover effects
        self.default_bg = bg
        self.hover_bg = hover_bg
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
        # Tooltip
        if tooltip:
            ToolTip(self, tooltip)
    
    def on_enter(self, e):
        if self['state'] != tk.DISABLED:
            self['background'] = self.hover_bg
    
    def on_leave(self, e):
        self['background'] = self.default_bg


class Section(tk.Frame):
    """Sección con título y separador visual"""
    def __init__(self, parent, title):
        super().__init__(parent, bg=AppStyles.colors['bg_medium'])
        
        separator = tk.Frame(self, bg=AppStyles.colors['bg_dark'], height=1)
        separator.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Label(
            self, text=title, 
            bg=AppStyles.colors['bg_medium'],
            fg=AppStyles.colors['accent'], 
            font=AppStyles.fonts['heading']
        ).pack(anchor=tk.W, padx=15, pady=(0, 10))


class LabeledSlider(tk.Frame):
    """Slider con etiqueta y valor dinámico"""
    def __init__(self, parent, label, variable, from_, to, value_func, resolution=1, tooltip=None):
        super().__init__(parent, bg=AppStyles.colors['bg_medium'])
        
        label_frame = tk.Frame(self, bg=AppStyles.colors['bg_medium'])
        label_frame.pack(fill=tk.X)
        
        label_widget = tk.Label(
            label_frame, text=label, 
            bg=AppStyles.colors['bg_medium'],
            fg=AppStyles.colors['text'], 
            font=AppStyles.fonts['body']
        )
        label_widget.pack(side=tk.LEFT)
        
        if tooltip:
            ToolTip(label_widget, tooltip)
        
        self.value_label = tk.Label(
            label_frame, text=value_func(None),
            bg=AppStyles.colors['bg_medium'],
            fg=AppStyles.colors['accent'],
            font=AppStyles.fonts['label']
        )
        self.value_label.pack(side=tk.RIGHT)
        
        self.scale = tk.Scale(
            self, from_=from_, to=to, 
            orient=tk.HORIZONTAL, 
            variable=variable,
            bg=AppStyles.colors['bg_medium'], 
            fg=AppStyles.colors['text'],
            highlightthickness=0, 
            resolution=resolution, 
            showvalue=0,
            troughcolor=AppStyles.colors['bg_dark'],
            activebackground=AppStyles.colors['accent'], 
            cursor="hand2",
            command=lambda v: self.value_label.config(text=value_func(v))
        )
        self.scale.pack(fill=tk.X)


class StatusBar(tk.Frame):
    """Barra de estado con iconos y mensajes"""
    def __init__(self, parent):
        super().__init__(parent, bg=AppStyles.colors['bg_dark'], height=30)
        self.pack_propagate(False)
        
        self.status_label = tk.Label(
            self, text="● Listo", 
            bg=AppStyles.colors['bg_dark'],
            fg=AppStyles.colors['success'], 
            font=AppStyles.fonts['body'],
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=15)
        
        self.info_label = tk.Label(
            self, text="", 
            bg=AppStyles.colors['bg_dark'],
            fg=AppStyles.colors['text_dim'], 
            font=AppStyles.fonts['body'],
            anchor=tk.E
        )
        self.info_label.pack(side=tk.RIGHT, padx=15)
    
    def set_status(self, message, color='success'):
        """Actualiza el estado con color"""
        colors = {
            'success': AppStyles.colors['success'],
            'warning': AppStyles.colors['warning'],
            'danger': AppStyles.colors['danger'],
            'info': AppStyles.colors['accent']
        }
        
        self.status_label.config(
            text=f"● {message}",
            fg=colors.get(color, AppStyles.colors['text'])
        )
    
    def set_info(self, message):
        """Actualiza información adicional"""
        self.info_label.config(text=message)


class ProgressPanel(tk.Frame):
    """Panel de progreso con barra y mensaje"""
    def __init__(self, parent):
        super().__init__(parent, bg=AppStyles.colors['bg_medium'])
        
        self.message_label = tk.Label(
            self, text="",
            bg=AppStyles.colors['bg_medium'],
            fg=AppStyles.colors['text'],
            font=AppStyles.fonts['body']
        )
        
        from tkinter import ttk
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=AppStyles.colors['bg_dark'],
            background=AppStyles.colors['accent'],
            bordercolor=AppStyles.colors['bg_dark'],
            lightcolor=AppStyles.colors['accent'],
            darkcolor=AppStyles.colors['accent']
        )
        
        self.progress_bar = ttk.Progressbar(
            self, 
            mode='indeterminate',
            style="Custom.Horizontal.TProgressbar"
        )
    
    def show(self, message="Procesando..."):
        """Muestra el panel de progreso"""
        self.message_label.config(text=message)
        self.message_label.pack(fill=tk.X, padx=15, pady=(10, 5))
        self.progress_bar.pack(fill=tk.X, padx=15, pady=(0, 10))
        self.progress_bar.start(10)
        self.pack(fill=tk.X, padx=15, pady=5)
    
    def update_message(self, message):
        """Actualiza el mensaje sin reiniciar la animación"""
        self.message_label.config(text=message)
    
    def hide(self):
        """Oculta el panel de progreso"""
        self.progress_bar.stop()
        self.pack_forget()
