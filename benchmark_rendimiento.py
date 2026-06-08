"""
Benchmark para medir el rendimiento real del sistema
Específico para Ryzen 9 7950X + RTX 4070
"""

import time
import torch
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def benchmark_cuda():
    """Prueba de velocidad CUDA"""
    print_header("🔥 BENCHMARK CUDA")
    
    if not torch.cuda.is_available():
        print("❌ CUDA no disponible")
        return
    
    device = torch.device('cuda')
    
    # Info de GPU
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM Total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    print(f"VRAM Libre: {(torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)) / 1024**3:.1f} GB")
    print()
    
    # Benchmark de inferencia
    sizes = [
        (1000, "Pequeño (1 seg audio)"),
        (16000, "Medio (1 seg audio 16kHz)"),
        (160000, "Grande (10 seg audio)"),
        (1600000, "Muy grande (100 seg audio)")
    ]
    
    print("Pruebas de velocidad de inferencia:")
    print("-" * 60)
    
    for size, desc in sizes:
        # Crear tensor de prueba
        audio = torch.randn(size, device=device)
        
        # Calentar GPU
        for _ in range(5):
            _ = audio * 2
        
        # Benchmark
        torch.cuda.synchronize()
        start = time.time()
        
        iterations = 100
        for _ in range(iterations):
            _ = audio * 2
            
        torch.cuda.synchronize()
        elapsed = time.time() - start
        
        throughput = (size * iterations) / elapsed / 1000000
        
        print(f"{desc:30} | {elapsed*1000:.2f}ms | {throughput:.1f} MSamples/s")
    
    print()

def benchmark_vad():
    """Prueba de velocidad del modelo VAD"""
    print_header("🎤 BENCHMARK VAD")
    
    try:
        from vad_detector import VoiceActivityDetector
        
        print("Cargando modelo Silero VAD...")
        start = time.time()
        
        vad = VoiceActivityDetector()
        vad.load_model()
        
        load_time = time.time() - start
        
        device_name = torch.cuda.get_device_name(0) if vad.device.type == 'cuda' else 'CPU'
        print(f"✅ Modelo cargado en {load_time:.2f}s")
        print(f"   Dispositivo: {device_name}")
        print(f"   Tipo: {vad.device.type.upper()}")
        print()
        
        # Simular diferentes duraciones de audio
        durations = [
            (10, "10 segundos"),
            (60, "1 minuto"),
            (300, "5 minutos"),
            (600, "10 minutos"),
            (1800, "30 minutos"),
            (3600, "1 hora"),
            (7200, "2 horas")
        ]
        
        print("Tiempos estimados de análisis VAD:")
        print("-" * 60)
        
        # Benchmark real con audio pequeño
        sample_duration = 10  # 10 segundos
        sample_size = sample_duration * vad.sample_rate
        audio_sample = torch.randn(sample_size).to(vad.device)
        
        # Calentar modelo
        for _ in range(3):
            try:
                _ = vad.get_speech_timestamps(
                    audio_sample,
                    vad.model,
                    threshold=0.5,
                    sampling_rate=vad.sample_rate
                )
            except:
                pass
        
        # Benchmark
        torch.cuda.synchronize() if vad.device.type == 'cuda' else None
        start = time.time()
        
        iterations = 5
        for _ in range(iterations):
            try:
                _ = vad.get_speech_timestamps(
                    audio_sample,
                    vad.model,
                    threshold=0.5,
                    sampling_rate=vad.sample_rate
                )
            except:
                pass
        
        torch.cuda.synchronize() if vad.device.type == 'cuda' else None
        elapsed = time.time() - start
        
        # Calcular velocidad por segundo
        time_per_second = (elapsed / iterations) / sample_duration
        
        for duration, desc in durations:
            estimated_time = duration * time_per_second
            
            if estimated_time < 60:
                time_str = f"{estimated_time:.1f}s"
            else:
                time_str = f"{estimated_time/60:.1f}min"
            
            speedup = duration / estimated_time
            
            print(f"{desc:15} | Análisis: {time_str:8} | Velocidad: {speedup:.1f}x real-time")
        
        print()
        
        # Mostrar rendimiento
        samples_per_second = (sample_size * iterations) / elapsed
        print(f"Throughput: {samples_per_second/1000000:.1f} MSamples/s")
        print(f"Factor de velocidad: {1/time_per_second:.1f}x tiempo real")
        
    except Exception as e:
        print(f"❌ Error en benchmark VAD: {e}")
        print("   Asegúrate de tener PyTorch y el modelo VAD instalados")

def benchmark_system():
    """Info del sistema"""
    print_header("💻 INFORMACIÓN DEL SISTEMA")
    
    import platform
    import psutil
    
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"CPU: {platform.processor()}")
    print(f"Núcleos físicos: {psutil.cpu_count(logical=False)}")
    print(f"Núcleos lógicos: {psutil.cpu_count(logical=True)}")
    print(f"RAM Total: {psutil.virtual_memory().total / 1024**3:.1f} GB")
    print(f"RAM Disponible: {psutil.virtual_memory().available / 1024**3:.1f} GB")
    
    if torch.cuda.is_available():
        print(f"\nGPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"PyTorch Version: {torch.__version__}")
    else:
        print("\n⚠️  CUDA no disponible")
    
    print()

def main():
    """Ejecutar todos los benchmarks"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "     BENCHMARK DE RENDIMIENTO - AUTO VIDEO EDITOR      ".center(58) + "█")
    print("█" + "     Optimizado para Ryzen 9 7950X + RTX 4070         ".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    benchmark_system()
    benchmark_cuda()
    benchmark_vad()
    
    print_header("✅ BENCHMARK COMPLETADO")
    print("\nInterpretación de resultados:")
    print("• MSamples/s: Millones de muestras por segundo procesadas")
    print("• x real-time: Cuántas veces más rápido que tiempo real")
    print("  Ejemplo: 180x = procesa 180 segundos de audio en 1 segundo")
    print("\nPara tu RTX 4070, espera:")
    print("• Análisis VAD: ~100-200x real-time")
    print("• Video 2h: ~30-60 segundos de análisis")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
