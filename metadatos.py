import json
import subprocess

def extraer_metadatos(ruta_video, ruta_ffprobe):
    """Obtiene la duración, pistas de audio y subtítulos del video usando FFprobe.

    Devuelve:
        (float: duracion_segundos, str: idiomas_audio, str: idiomas_subtitulos)
    """
    comando = [
        ruta_ffprobe, "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", ruta_video
    ]
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, encoding='utf-8')
        data = json.loads(resultado.stdout)

        duracion = float(data.get('format', {}).get('duration', 0.0))
        audios = []
        subtitulos = []

        for stream in data.get('streams', []):
            tipo = stream.get('codec_type')
            tags = stream.get('tags', {})
            lang = tags.get('language', 'und').upper()

            if tipo == 'audio':
                audios.append(lang)
            elif tipo == 'subtitle':
                disposition = stream.get('disposition', {})
                forced = "[FORZADO]" if disposition.get('forced') == 1 else ""
                subtitulos.append(f"{lang}{forced}")

        idiomas_audio = ", ".join(audios) if audios else "Ninguna"
        idiomas_subs = ", ".join(subtitulos) if subtitulos else "Ninguno"

        return duracion, idiomas_audio, idiomas_subs

    except Exception as e:
        # En caso de error de lectura, devuelve valores seguros para evitar cuelgues
        return 0.0, f"Error de lectura ({str(e)})", "Error de lectura"
