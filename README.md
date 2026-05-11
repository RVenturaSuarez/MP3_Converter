# TubeGet

[![Release](https://img.shields.io/github/v/release/RVenturaSuarez/TubeGet?color=blue)](https://github.com/RVenturaSuarez/TubeGet/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/Windows-10%2B-blue)](https://github.com/RVenturaSuarez/TubeGet/releases/latest)

Convierte videos de YouTube a MP3 o MP4 en un clic. Portable, sin instalacion.

---

## Descargar (1 clic)

**[Descargar TubeGet.exe](https://github.com/RVenturaSuarez/TubeGet/releases/latest/download/TubeGet.exe)**

Un solo archivo. Doble clic y listo. No requiere Python, FFmpeg ni nada.

---

## Caracteristicas

- Extrae audio a **MP3** con caratula y metadatos
- Descarga **MP4** con resolucion 360p / 720p / 1080p
- Calidad MP3: 128 / 192 / 256 / 320 kbps
- Soporte para **playlists** completas
- **Cancelar** descarga en cualquier momento
- Barra de progreso en tiempo real
- Modo oscuro, todas las opciones visibles sin desplegables
- **Portable**: un solo .exe, no requiere instalacion

## Como usar

1. Descarga el .exe del enlace de arriba
2. Doble clic (no requiere instalacion)
3. Pega el link del video de YouTube
4. Selecciona MP3 o MP4 con los radio buttons
5. Elige calidad
6. Clic en **DESCARGAR**

El archivo aparece en tu carpeta de musica con caratula incluida (MP3).

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
