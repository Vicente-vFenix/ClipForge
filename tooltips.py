import tkinter as tk

class ToolTip:
    """
    Tooltip que aparece al pasar el ratón sobre un widget
    """
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.after_id = None
        
        self.widget.bind("<Enter>", self.schedule_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<Button>", self.hide_tooltip)
    
    def schedule_tooltip(self, event=None):
        """Programa la aparición del tooltip después del delay"""
        self.hide_tooltip()
        self.after_id = self.widget.after(self.delay, self.show_tooltip)
    
    def show_tooltip(self):
        """Muestra el tooltip"""
        if self.tooltip_window:
            return
        
        # Posición del tooltip
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Crear ventana del tooltip
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Contenido del tooltip
        frame = tk.Frame(self.tooltip_window, 
                        background="#2d2d2d",
                        borderwidth=1,
                        relief=tk.SOLID)
        frame.pack()
        
        label = tk.Label(frame,
                        text=self.text,
                        justify=tk.LEFT,
                        background="#2d2d2d",
                        foreground="#ffffff",
                        font=('Segoe UI', 9),
                        padx=10,
                        pady=8,
                        wraplength=300)
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Oculta el tooltip"""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def add_tooltip(widget, text, delay=500):
    """
    Función helper para agregar tooltips fácilmente
    
    Uso:
        add_tooltip(mi_slider, "Mayor valor = menos sensible")
    """
    return ToolTip(widget, text, delay)
