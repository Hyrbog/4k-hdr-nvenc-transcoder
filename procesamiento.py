import os
import sys
import re
import subprocess
import logging
from colorama import Fore

from metadatos import extraer_metadatos
from interfaz import parsear_tiempo, mostrar_barra_progreso
from gestor_archivos import finalizar_almacenamiento_video
from configuracion import registrar_video_corrupto, RUTA_FFMPEG, RUTA_FFPROBE  # <-- IMPORTANTE: Importar rutas aquí

def procesar_video_individual(params_video, params_globales, gestor_tiempos, config_usuario):
    """
    Ejecuta la transcodificación de un video individual aplicando las configuraciones elegidas.
    """
    # Despaquetar parámetros (Ahora coinciden perfectamente con los 7 elementos enviados)
    carpeta, archivo, ruta_de_trabajo, archivo_trabajo_nombre, duracion_total, codec_real, es_hdr = params_video
    i_carp, carpetas, num_video, videos_4k_reales, total_videos_global_pendientes, ruta_salida_res, ruta_salida_hechos = params_globales
    bitrate_elegido, resolucion_elegida, config_corregir_hdr = config_usuario

    # 1. CONSTRUCCIÓN INTELIGENTE DEL NOMBRE SEGÚN LA RESOLUCIÓN SELECCIONADA
    nombre_limpio = archivo_trabajo_nombre.replace(".mp4", ".mkv").replace(".MP4", ".mkv")

    # Reemplazar etiquetas de resolución dinámicamente en el nombre
    res_tag = "4k" if resolucion_elegida == "4k" else ("720p" if resolucion_elegida == "720p" else "1080p")
    nombre_limpio = re.sub(r'(?i)2160p|4k|1080p|720p', res_tag, nombre_limpio)

    # Mantener o forzar la etiqueta x265
    if "x264" in nombre_limpio.lower() or "x265" in nombre_limpio.lower():
        nuevo_nombre = nombre_limpio.replace("x264", "x265").replace("X264", "x265")
    else:
        nombre_sin_ext, ext_mkv = os.path.splitext(nombre_limpio)
        nuevo_nombre = f"{nombre_sin_ext} - x265{ext_mkv}"

    ruta_temporal = os.path.join(carpeta, f"temp_{nuevo_nombre}")
    ruta_destino_final = os.path.join(ruta_salida_res, nuevo_nombre)
    ruta_original_hechos = os.path.join(ruta_salida_hechos, archivo)

    # Extraer metadatos de audio y subs (Pasamos RUTA_FFPROBE que importamos arriba)
    _, idiomas_audio, idiomas_subs = extraer_metadatos(ruta_de_trabajo, RUTA_FFPROBE)

    # Evaluar la condición del HDR solicitada (Mejora 3)
    aplicar_filtro_bt709 = es_hdr and config_corregir_hdr

    print(f"\n{Fore.YELLOW}--------------------------------------------------")
    print(f"{Fore.YELLOW} PROCESANDO VIDEO ({num_video} / {len(videos_4k_reales)})")
    print(f"{Fore.YELLOW}--------------------------------------------------")
    print(f"{Fore.WHITE}• Archivo Origen:  {Fore.LIGHTBLACK_EX}{archivo_trabajo_nombre}")
    print(f"{Fore.WHITE}• Nombre Final:    {Fore.LIGHTWHITE_EX}{nuevo_nombre}")
    print(f"{Fore.WHITE}• Códec Detectado: {Fore.MAGENTA}{codec_real.upper()}")
    print(f"{Fore.WHITE}• Perfil de Color: {Fore.GREEN}{'HDR -> Convertir a BT.709' if aplicar_filtro_bt709 else ('HDR Original (Sin cambios)' if es_hdr else 'SDR Directo')}")
    print(f"{Fore.WHITE}• Res. Objetivo:   {Fore.CYAN}{res_tag.upper()}")
    print(f"{Fore.WHITE}• Bitrate Target:  {Fore.CYAN}{bitrate_elegido}")
    print(f"{Fore.WHITE}• Audio (Idiom):   {Fore.GREEN}{idiomas_audio}")
    print(f"{Fore.WHITE}• Subtítulos:      {Fore.GREEN}{idiomas_subs}")
    print(f"{Fore.YELLOW}--------------------------------------------------")

    if aplicar_filtro_bt709:
        print(f"{Fore.CYAN}Paso 1/3: Aplicando Tonemapping HDR -> BT.709 y reescalando...")
    else:
        print(f"{Fore.CYAN}Paso 1/3: Reescalando video directo...")

    # Disparar cronómetro del video actual
    gestor_tiempos.iniciar_reloj_video()

    # 2. CONFIGURACIÓN ESTABLE DE FILTROS HÍBRIDOS (Evita cuelgues de CUDA)
    lista_filtros = []
    if aplicar_filtro_bt709:
        # El mapeo 'hable' por software para fijar los colores BT.709
        lista_filtros.append("zscale=t=linear:matrix=bt2020nc,tonemap=tonemap=hable:desat=2,zscale=p=bt709:t=bt709:m=bt709,format=yuv420p")

    if resolucion_elegida == "1080p":
        lista_filtros.append("scale=1920:1080")
    elif resolucion_elegida == "720p":
        lista_filtros.append("scale=1280:720")

    filtros_video = ",".join(lista_filtros)

    # 3. PREPARACIÓN DEL COMANDO FFMPEG ESTABLE CON CODIFICACIÓN NVENC (RTX 4090)
    # Eliminamos los argumentos conflictivos de decodificación por hardware directa para dar máxima estabilidad
    comando_ffmpeg = [
        RUTA_FFMPEG, "-y", "-i", ruta_de_trabajo, "-map", "0"
    ]

    if filtros_video:
        comando_ffmpeg.extend(["-vf", filtros_video])

    # La RTX 4090 se encargará del 90% del trabajo pesado aquí al comprimir en HEVC/x265 por hardware
    comando_ffmpeg.extend(["-c:v", "hevc_nvenc", "-preset", "p4"])

    # Gestión de Bitrate adaptada a NVENC
    if str(bitrate_elegido).lower() in ["5", "original"]:
        # Constant Quality (CQ) a 22 mantiene una fidelidad visual perfecta comparada al original sin engordar el archivo
        comando_ffmpeg.extend(["-rc", "constqp", "-qp", "22"])
    else:
        comando_ffmpeg.extend(["-b:v", str(bitrate_elegido)])

    # Copiar audio y subtítulos intactos
    comando_ffmpeg.extend(["-c:a", "copy", "-c:s", "copy", "-max_interleave_delta", "0", ruta_temporal])

    # 4. EJECUCIÓN Y MONITOREO EN TIEMPO REAL
    proceso = subprocess.Popen(
        comando_ffmpeg, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, encoding='utf-8', errors='ignore'
    )

    regex_tiempo = re.compile(r"time=(\d{2}:\d{2}:\d{2}\.\d{2})")
    regex_fps = re.compile(r"fps=\s*(\d+)")
    regex_speed = re.compile(r"speed=\s*([\d.]+x)")

    fps_actual = "0"
    velocidad_actual = "1.0x"
    velocidad_num_media = 1.0
    segundos_ya_procesados_carpeta = 0.0
    duracion_total_carpeta = sum(d for _, d in videos_4k_reales)

    while True:
        linea = proceso.stdout.readline()
        if not linea and proceso.poll() is not None:
            break

        match_t = regex_tiempo.search(linea)
        match_f = regex_fps.search(linea)
        match_s = regex_speed.search(linea)

        if match_f:
            fps_actual = match_f.group(1)
        if match_s:
            velocidad_actual = match_s.group(1)
            try:
                velocidad_num_media = max(0.1, float(velocidad_actual.replace('x', '')))
            except ValueError:
                pass

        if match_t:
            segundos_convertidos = parsear_tiempo(match_t.group(1))

            eta_v, eta_c, eta_g = gestor_tiempos.calcular_etas(
                segundos_convertidos, duracion_total,
                duracion_total_carpeta, segundos_ya_procesados_carpeta,
                velocidad_num_media
            )

            if segundos_convertidos >= duracion_total or eta_c == "00:00:00":
                if i_carp < len(carpetas):
                    segundos_restantes_global = max(
                        0.0,
                        gestor_tiempos.duracion_total_global - (gestor_tiempos.segundos_ya_procesados_global + segundos_convertidos)
                    )
                    eta_g_segundos = segundos_restantes_global / velocidad_num_media
                    horas_g = int(eta_g_segundos) // 3600
                    min_g = (int(eta_g_segundos) % 3600) // 60
                    seg_g = int(eta_g_segundos) % 60
                    eta_g = f"{horas_g:02d}:{min_g:02d}:{seg_g:02d}"

            paquete_ticks = (eta_v, eta_c, eta_g, len(videos_4k_reales), total_videos_global_pendientes)
            mostrar_barra_progreso(segundos_convertidos, duracion_total, fps_actual, velocidad_actual, ticks_restantes=paquete_ticks)

    proceso.wait()

    # Finalizar y limpiar consola
    paquete_ceros, tiempo_transcurrido = gestor_tiempos.finalizar_video(
        duracion_total, len(videos_4k_reales), total_videos_global_pendientes
    )
    mostrar_barra_progreso(
        duracion_total, duracion_total, fps_actual, velocidad_actual,
        ticks_restantes=paquete_ceros, forzar_100=True
    )

    sys.stdout.write("\n\033[K")

    print(f"{Fore.GREEN}✔ Conversión completada correctamente.")
    print(f"{Fore.LIGHTBLUE_EX}⏱ Tiempo transcurrido en la conversión: {Fore.WHITE}{tiempo_transcurrido}\n")

    if proceso.returncode == 0 and os.path.exists(ruta_temporal):
        finalizar_almacenamiento_video(
            carpeta, archivo, ruta_temporal, ruta_destino_final, ruta_de_trabajo, ruta_original_hechos
        )
        logging.info(f"Video convertido con éxito: {archivo}")
    else:
        print(f"{Fore.RED}[ERROR] La conversión de '{archivo}' ha fallado.")
        registrar_video_corrupto(carpeta, archivo, "Fallo crítico en FFmpeg", proceso.returncode)
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)
