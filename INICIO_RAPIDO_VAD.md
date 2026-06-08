# 🚀 Inicio Rápido - Detección de Voz con IA

## ⏱️ En 5 minutos

### 1. Instalar dependencias (solo primera vez)

```bash
instalar_vad.bat
```

O manualmente:
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. Verificar instalación (opcional)

```bash
python test_vad.py
```

### 3. Usar el programa

1. **Ejecuta** `main.py` o `AutoVideoEditor.bat`
2. **Carga tu video**
3. **Selecciona el canal de audio** con tu voz
4. Verifica que **"🎤 Detección de voz con IA"** esté activado ✅ (viene por defecto)
5. Ajusta si quieres:
   - **Duración mínima**: 1.5-2.0s (cuánto silencio mínimo para cortar)
   - **Margen**: 0.3-0.5s (espacio extra para no cortar palabras)
6. Click en **"🔍 Detectar Pausas"**
7. Espera unos segundos (primera vez descarga modelo ~1.5MB)
8. Revisa los segmentos detectados en la línea de tiempo
9. Click en **"🚀 EXPORTAR VIDEO"**

## 🎯 ¿Qué hace el modo IA?

**ANTES (modo clásico):**
- Detectaba cualquier sonido fuerte
- ❌ Capturaba teclas del teclado
- ❌ Capturaba clics del ratón
- ❌ Necesitaba mucho ajuste manual

**AHORA (modo IA):**
- ✅ Detecta SOLO voz humana
- ✅ Ignora teclas del teclado
- ✅ Ignora clics del ratón
- ✅ Ignora ruidos de fondo
- ✅ Funciona automáticamente

## 📊 Comparación práctica

### Ejemplo: Tutorial de programación

**Sin VAD:**
```
[Tu voz] → DETECTA ✅
[Tecleo] → DETECTA ❌ (problema!)
[Clic]   → DETECTA ❌ (problema!)
[Pausa]  → no detecta ✅
```

**Con VAD:**
```
[Tu voz] → DETECTA ✅
[Tecleo] → no detecta ✅ (¡perfecto!)
[Clic]   → no detecta ✅ (¡perfecto!)
[Pausa]  → no detecta ✅
```

## ⚙️ Configuración recomendada

### Para tutoriales con tecleo
- ✅ VAD activado
- Duración mínima: 1.5s
- Margen: 0.3s

### Para vlogs con ruido ambiente
- ✅ VAD activado
- Duración mínima: 2.0s
- Margen: 0.5s

### Para podcasts/entrevistas
- ✅ VAD activado
- Duración mínima: 2.0s
- Margen: 0.5s

### Si solo quieres cortar silencios largos (sin VAD)
- ❌ VAD desactivado (modo clásico)
- Sensibilidad: -30dB
- Duración mínima: 3.0s
- Margen: 0.5s

## 🔧 Solución rápida de problemas

### "No se detectó voz humana"
- ¿Seleccionaste el canal correcto de audio?
- ¿Tu voz se escucha en el video?
- Prueba otro canal de audio

### Primera vez tarda mucho
- Normal, está descargando el modelo (~1.5MB)
- Solo pasa una vez
- Las siguientes veces es instantáneo

### Quiero el modo antiguo
- Simplemente desactiva ☐ "Detección de voz con IA"
- Los controles antiguos aparecerán

## 💡 Tip profesional

Si grabas tutoriales o streams:
1. Usa un micrófono decente (no el del laptop)
2. Ponlo cerca de tu boca
3. Reduce ruidos fuertes del ambiente
4. Activa VAD → ¡y listo!

El resultado será mucho mejor que antes, sin necesidad de ajustar nada manualmente.

## 📺 Diferencia visual

**Antes:**
```
█████░░███████░█░░░█████████  ← Detecta todo
```

**Después:**
```
█████░░░░░░███░░░░░░███████  ← Solo tu voz
```

## 🎓 Más información

Lee el **README_VAD.md** completo para:
- Detalles técnicos del modelo
- Casos de uso específicos
- Parámetros avanzados
- Solución de problemas detallada

---

**¡Listo! Ya tienes detección de voz profesional con IA 🎉**
