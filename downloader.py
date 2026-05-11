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


def descargar(url, output_path, formato="mp3", calidad="192",
              incluir_caratula=True, descargar_lista=False, cancel_event=None,
              progress_callback=None, item_done_callback=None,
              done_callback=None, error_callback=None):
    """
    Descarga de YouTube a MP3 o MP4.

    Args:
        url: URL del video o playlist
        output_path: Carpeta de destino
        formato: 'mp3' o 'mp4'
        calidad: bitrate kbps (mp3) o altura px (mp4)
        incluir_caratula: Solo para mp3, incrusta miniatura
        descargar_lista: Procesar playlist completa
        cancel_event: threading.Event para cancelar
        progress_callback, item_done_callback, done_callback, error_callback
    """
    def _hook(d):
        if cancel_event and cancel_event.is_set():
            raise CancelDownload("Descarga cancelada por el usuario")
        if progress_callback:
            progress_callback(d)

    _completados = set()

    def _post_hook(d):
        if d['status'] == 'finished' and item_done_callback:
            info = d.get('info_dict', {})
            pl_idx = info.get('playlist_index')
            if pl_idx is not None and pl_idx not in _completados:
                _completados.add(pl_idx)
                title = info.get('title', 'audio')
                safe_title = _sanitize_filename(title)
                ext = formato
                mp_path = os.path.join(output_path, f"{safe_title}.{ext}")
                pl_count = info.get('playlist_count')
                item_done_callback(pl_idx, pl_count, title, mp_path)

    if formato == "mp4":
        ydl_opts = {
            'format': f'best[height<={calidad}]',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [_hook],
            'postprocessor_hooks': [_post_hook],
            'socket_timeout': 30,
            'noplaylist': not descargar_lista,
            'quiet': True,
        }
    else:
        postprocessors = [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': f'{calidad}k'},
            {'key': 'FFmpegMetadata', 'postprocessor_args': {'id3v2_version': '3'}},
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
            titulos = [e.get('title', 'audio') for e in info]
            if done_callback:
                done_callback(None, f"{len(info)} videos descargados")
        else:
            title = info.get('title', 'audio')
            safe_title = _sanitize_filename(title)
            ext = formato
            filepath = os.path.join(output_path, f"{safe_title}.{ext}")
            if done_callback:
                done_callback(filepath, title)

    except CancelDownload:
        if error_callback:
            error_callback("Descarga cancelada")
    except Exception as e:
        if error_callback:
            error_callback(str(e))
