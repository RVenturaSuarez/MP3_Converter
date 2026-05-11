import os
import sys
import re
import threading
import yt_dlp


class CancelDownload(Exception):
    pass


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
                  descargar_lista=False, cancel_event=None,
                  progress_callback=None, item_done_callback=None,
                  done_callback=None, error_callback=None):
    """
    Descarga audio de YouTube y lo convierte a MP3.

    Args:
        url: URL del video o playlist
        output_path: Carpeta de destino
        calidad: Calidad en kbps ('128', '192', '256', '320')
        incluir_caratula: Incrustar miniatura en el MP3
        descargar_lista: Si es True, procesa la playlist completa
        cancel_event: threading.Event para cancelar la descarga
        progress_callback: Llamado con dict de progreso de yt-dlp
        item_done_callback: Llamado con (indice, total, titulo, ruta_mp3) por cada item de playlist
        done_callback: Llamado con (ruta_mp3, titulo) al terminar (single) o None para playlist
        error_callback: Llamado con (mensaje_error) si falla
    """
    def _hook(d):
        if cancel_event and cancel_event.is_set():
            raise CancelDownload("Descarga cancelada por el usuario")
        if progress_callback:
            progress_callback(d)

    _completados = set()

    def _post_hook(d):
        """Se dispara cuando un item de playlist termina (descarga + postprocesado)."""
        if d['status'] == 'finished' and item_done_callback:
            info = d.get('info_dict', {})
            pl_idx = info.get('playlist_index')
            if pl_idx is not None and pl_idx not in _completados:
                _completados.add(pl_idx)
                title = info.get('title', 'audio')
                safe_title = _sanitize_filename(title)
                mp3_path = os.path.join(output_path, f"{safe_title}.mp3")
                pl_count = info.get('playlist_count')
                item_done_callback(pl_idx, pl_count, title, mp3_path)

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
        'postprocessor_hooks': [_post_hook],
        'socket_timeout': 30,
        'noplaylist': not descargar_lista,
        'quiet': True,
    }

    ffmpeg_dir = _get_ffmpeg_dir()
    if ffmpeg_dir:
        ydl_opts['ffmpeg_location'] = ffmpeg_dir

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        if isinstance(info, list):
            # Playlist: item_done_callback ya fue llamado por cada video
            titulos = [e.get('title', 'audio') for e in info]
            if done_callback:
                done_callback(None, f"{len(info)} videos descargados")
        else:
            title = info.get('title', 'audio')
            safe_title = _sanitize_filename(title)
            mp3_path = os.path.join(output_path, f"{safe_title}.mp3")
            if done_callback:
                done_callback(mp3_path, title)

    except CancelDownload:
        if error_callback:
            error_callback("Descarga cancelada")
    except Exception as e:
        if error_callback:
            error_callback(str(e))
