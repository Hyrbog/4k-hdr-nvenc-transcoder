import os
import subprocess
import json
import shutil
import logging
from colorama import Fore
from interfaz import mostrar_aviso_remux

# Ruta de MKVToolNix
RUTA_MKVMERGE = shutil.which("mkvmerge") or r"C:\Tools\MKVToolNix\mkvmerge.exe"

def asegurar_mkv(ruta_video, carpeta_base):
    """
    Si el video es MP4, usa mkvmerge para meterlo en un contenedor MKV
    dentro de 'Pasados de MP4 a MKV'. Devuelve la nueva ruta del MKV.
    """
    nombre_archivo = os.path.basename(ruta_video)
    nombre_sin_ext, ext = os.path.splitext(nombre_archivo)

    if ext.lower() == '.mkv':
        return ruta_video

    if ext.lower() == '.mp4':
        carpeta_destino = os.path.join(carpeta_base, "Pasados de MP4 a MKV")
        # LLAMAMOS AL NUEVO AVISO VISUAL DE LA INTERFAZ
        mostrar_aviso_remux(nombre_archivo, carpeta_destino)
        os.makedirs(carpeta_destino, exist_ok=True)

        nueva_ruta_mkv = os.path.join(carpeta_destino, f"{nombre_sin_ext}.mkv")

        if os.path.exists(nueva_ruta_mkv):
            return nueva_ruta_mkv

        print(f"{Fore.YELLOW}  [MP4 DETECTADO] Transvasando '{nombre_archivo}' a MKV con MKVToolNix...")
        logging.info(f"Remuxing MP4 a MKV: {nombre_archivo}")

        comando = [RUTA_MKVMERGE, "-o", nueva_ruta_mkv, ruta_video]

        try:
            resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if resultado.returncode in [0, 1]:
                print(f"{Fore.GREEN}  [ÉXITO] Video preparado en: {nueva_ruta_mkv}")
                return nueva_ruta_mkv
            else:
                print(f"{Fore.RED}  [ERROR] mkvmerge falló. Código: {resultado.returncode}")
                return None
        except Exception as e:
            print(f"{Fore.RED}  [ERROR] No se pudo ejecutar mkvmerge: {e}")
            return None

    return None

def analizar_propiedades_video(ruta_video, ruta_ffprobe):
    """
    Examina el video internamente con FFprobe.
    Devuelve una tupla: (es_hdr [True/False], codec_real ['x265', 'x264', 'desconocido'])
    """
    comando = [
        ruta_ffprobe, "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,color_space,color_transfer,color_primaries",
        "-of", "json", ruta_video
    ]

    es_hdr = False
    codec_real = "desconocido"

    try:
        resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        datos = json.loads(resultado.stdout)

        if "streams" in datos and len(datos["streams"]) > 0:
            stream = datos["streams"][0]

            # 1. Identificar Códec
            codec_name = stream.get("codec_name", "").lower()
            if "hevc" in codec_name or "h265" in codec_name:
                codec_real = "x265"
            elif "h264" in codec_name:
                codec_real = "x264"

            # 2. Identificar si es HDR
            primarios = stream.get("color_primaries", "")
            transferencia = stream.get("color_transfer", "")
            if "2020" in primarios or "smpte2084" in transferencia or "arib-std-b67" in transferencia:
                es_hdr = True

    except Exception as e:
        logging.error(f"Error en ffprobe analizando propiedades de {ruta_video}: {e}")

    return es_hdr, codec_real
