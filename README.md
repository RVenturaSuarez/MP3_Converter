# MP3 Converter

Converti videos de YouTube a MP3 en un click. Con caratula, metadatos y calidad seleccionable.

## Caracteristicas

- Extrae audio de cualquier video de YouTube y lo convierte a MP3
- **Caratula incrustada** en el archivo (miniatura del video como portada)
- **Metadatos** automaticos: titulo, artista, album
- **Calidad seleccionable**: 128, 192, 256 o 320 kbps
- Barra de progreso en tiempo real
- Modo oscuro, interfaz moderna
- **Portable**: un solo .exe, sin instalar nada

## Como usar

1. Descarga **MP3_Converter.exe** de la seccion [Releases](https://github.com/tuusuario/MP3_Converter/releases)
2. Hace doble clic (no requiere instalacion)
3. Pega el link del video de YouTube
4. Opcional: elegi carpeta de destino y calidad
5. Click en **DESCARGAR MP3**
6. El archivo MP3 aparece en la carpeta elegida, con la portada del video

### Opciones

| Calidad         | Tamano (~3 min) | Recomendacion         |
|-----------------|----------------|-----------------------|
| 128 kbps        | ~3 MB           | Solo si falta espacio |
| 192 kbps        | ~4 MB           | **Recomendado**       |
| 256 kbps        | ~6 MB           | Para audiofilos       |
| 320 kbps        | ~8 MB           | Maxima calidad        |

## Requisitos (solo para desarrollo)

Si queres modificar el codigo o reconstruir el .exe:

```bash
pip install -r requirements.txt
python main.py

# Para generar el .exe portable:
.\build.bat
```

## Licencia

MIT -- usa, modifica y comparti libremente.
