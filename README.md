# MP3 Converter

[![Release](https://img.shields.io/github/v/release/RVenturaSuarez/MP3_Converter?color=blue)](https://github.com/RVenturaSuarez/MP3_Converter/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/Windows-10%2B-blue)](https://github.com/RVenturaSuarez/MP3_Converter/releases/latest)

Convierte videos de YouTube a MP3 en un clic. Portable, sin instalacion.

---

## Descargar (1 clic)

**[Descargar MP3_Converter.exe](https://github.com/RVenturaSuarez/MP3_Converter/releases/latest/download/MP3_Converter.exe)**

Un solo archivo. Doble clic y listo. No requiere Python, FFmpeg ni nada.

---

## Caracteristicas

- Extrae audio de YouTube y lo convierte a MP3
- **Caratula incrustada** en el archivo (miniatura del video como portada)
- **Calidad seleccionable**: 128, 192, 256 o 320 kbps
- **Soporte para playlists** completas
- **Cancelar** descarga en cualquier momento
- **Metadatos** automaticos: titulo, artista, album
- Barra de progreso en tiempo real con velocidad de descarga
- Modo oscuro, interfaz moderna
- **Portable**: un solo .exe, no requiere instalacion

## Como usar

1. Descarga el .exe del enlace de arriba
2. Doble clic (no requiere instalacion)
3. Pega el link del video de YouTube
4. Elige calidad y carpeta de destino (opcional)
5. Clic en **DESCARGAR MP3**

El archivo MP3 aparece en la carpeta elegida con la portada del video incluida.

### Calidades disponibles

| Calidad | Tamano (~3 min) | Recomendacion |
|---|---|---|
| 128 kbps | ~3 MB | Solo si falta espacio |
| **192 kbps** | ~4 MB | **Recomendado** |
| 256 kbps | ~6 MB | Para audiofilos |
| 320 kbps | ~8 MB | Maxima calidad |

## Desarrollo

Si queres modificar el codigo o reconstruir el .exe:

```bash
pip install -r requirements.txt
python main.py

# Para generar el .exe portable:
build.bat
```

## Licencia

MIT — libre para usar, modificar y compartir. Ver [LICENSE](LICENSE).
