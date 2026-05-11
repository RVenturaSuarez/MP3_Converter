import os
import sys
import re
import yt_dlp


def _sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()


def _tiene_mutagen():
    try:
        import mutagen
        return True
    except ImportError:
        return False


def _get_ffmpeg_dir():
    if getattr(sys, 'frozen', False):
        ffmpeg_path = os.path.join(sys._MEIPASS, 'ffmpeg', 'ffmpeg.exe')
        if os.path.isfile(ffmpeg_path):
            return os.path.dirname(ffmpeg_path)
    try:
        import imageio_ffmpeg
        return os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        return None


def descargar_mp3(url, output_path, calidad, incluir_caratula=True,
                  progress_callback=None, done_callback=None, error_callback=None):
    """
    Descarga audio de YouTube y lo convierte a MP3.

    Args:
        url: URL del video
        output_path: Carpeta de destino
        calidad: Calidad en kbps (str: '128', '192', '256', '320')
        incluir_caratula: Si es True intenta incrustar la miniatura del video
        progress_callback: Llamado con dict de progreso de yt-dlp
        done_callback: Llamado con (ruta_mp3, titulo) al terminar
        error_callback: Llamado con (mensaje_error) si falla
    """
    def _hook(d):
        if progress_callback:
            progress_callback(d)

    postprocessors = [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': calidad,
        },
        {'key': 'FFmpegMetadata'},
    ]

    if incluir_caratula and _tiene_mutagen():
        postprocessors.append({'key': 'EmbedThumbnail'})

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': postprocessors,
        'writethumbnail': incluir_caratula and _tiene_mutagen(),
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'progress_hooks': [_hook],
        'socket_timeout': 30,
        'quiet': True,
    }

    ffmpeg_dir = _get_ffmpeg_dir()
    if ffmpeg_dir:
        ydl_opts['ffmpeg_location'] = ffmpeg_dir

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio')
            safe_title = _sanitize_filename(title)
            mp3_path = os.path.join(output_path, f"{safe_title}.mp3")
            if done_callback:
                done_callback(mp3_path, title)
    except Exception as e:
        if error_callback:
            error_callback(str(e))
