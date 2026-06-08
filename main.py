import tkinter as tk
import sys
import logging
from pathlib import Path

# Configurar logging antes de importar otros módulos
log_file = Path.home() / 'video_editor_debug.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Punto de entrada principal de la aplicación"""
    try:
        logger.info("=" * 60)
        logger.info("Iniciando Auto Video Editor Pro")
        logger.info(f"Python {sys.version}")
        logger.info("=" * 60)
        
        # Importar después de configurar logging
        from editor_gui import EditorVideoApp
        
        # Crear ventana principal
        root = tk.Tk()
        
        # Configurar icono (si existe)
        try:
            icon_path = Path(__file__).parent / 'icon.ico'
            if icon_path.exists():
                root.iconbitmap(str(icon_path))
        except Exception as e:
            logger.debug(f"No se pudo cargar icono: {e}")
        
        # Crear aplicación
        app = EditorVideoApp(root)
        
        # Configurar cierre limpio
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Iniciar loop principal
        logger.info("Aplicación iniciada correctamente")
        root.mainloop()
        
        logger.info("Aplicación cerrada normalmente")
        
    except Exception as e:
        logger.critical(f"Error crítico en la aplicación: {e}", exc_info=True)
        
        # Mostrar error al usuario
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "Error Crítico",
                f"La aplicación encontró un error crítico:\n\n{str(e)}\n\n"
                f"Revisa el archivo de log:\n{log_file}"
            )
        except:
            print(f"ERROR CRÍTICO: {e}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
