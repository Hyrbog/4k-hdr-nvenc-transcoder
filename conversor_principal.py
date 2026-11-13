import os
import sys
import logging
from colorama import init, Fore

# Módulos del ecosistema original
from interfaz import limpiar_pantalla
from configuracion import (
    RUTA_FFMPEG, RUTA_FFPROBE, ARCHIVO_TXT, CARPETA_1080P,
    CARPETA_HECHOS, CARPETA_720P, CARPETA_4K, registrar_video_corrupto
)
from calculoTiempos import GestorTiempos
from gestor_archivos import escanear_cola_global
from comprobacionVideos import asegurar_mkv, analizar_propiedades_video

# NUEVAS IMPORTACIONES DE NUESTROS MÓDULOS DIVIDIDOS
from interaccion import solicitar_configuracion_video
from procesamiento import procesar_video_individual

# Inicializar colores en consola
init(autoreset=True)

# --- INICIO DEL PROCESO INTERACTIVO MEJORADO ---
config_usuario = solicitar_configuracion_video()
bitrate_elegido, resolucion_elegida, config_corregir_hdr = config_usuario

limpiar_pantalla()
print(f"{Fore.CYAN}==================================================")
print(f"{Fore.CYAN}         OPTIMIZADOR DE VIDEO MULTI-FORMATO       ")
print(f"{Fore.CYAN}==================================================")
logging.info("--- INICIO DE NUEVA SESIÓN DE CONVERSIÓN ---")

# Validaciones esenciales
if not os.path.exists(RUTA_FFMPEG) or not os.path.exists(RUTA_FFPROBE):
    print(f"{Fore.RED}[ERROR] No se encontró FFmpeg o FFprobe en las rutas.")
    sys.exit(1)

if not os.path.exists(ARCHIVO_TXT):
    print(f"{Fore.RED}[ERROR] No se encuentra el archivo de carpetas: {ARCHIVO_TXT}")
    sys.exit(1)

with open(ARCHIVO_TXT, 'r', encoding='utf-8') as f:
    carpetas = [linea.strip() for linea in f if linea.strip()]

# Escaneo modularizado
duracion_total_global, total_videos_global_pendientes, datos_carpetas = escanear_cola_global(carpetas, RUTA_FFPROBE)
gestor_tiempos = GestorTiempos(duracion_total_global)

# --- BUCLE PRINCIPAL DE CARPETAS ---
for i_carp, carpeta in enumerate(carpetas, 1):
    print(f"{Fore.MAGENTA}==================================================")
    print(f"{Fore.MAGENTA} CARPETA ({i_carp}/{len(carpetas)}): {carpeta}")
    print(f"{Fore.MAGENTA}==================================================")

    if not os.path.exists(carpeta):
        print(f"{Fore.RED}[ERROR] Carpeta inaccesible. Saltando...")
        continue

    videos_4k_reales = datos_carpetas.get(carpeta, [])
    if not videos_4k_reales:
        print(f"{Fore.YELLOW}-> No hay videos pendientes en esta carpeta.\n")
        continue

    # Determinar la carpeta de salida dinámicamente según la resolución seleccionada
    if resolucion_elegida == "4k":
        folder_salida = getattr(sys.modules[__name__], 'CARPETA_4K', 'Video_4K')
    elif resolucion_elegida == "720p":
        folder_salida = getattr(sys.modules[__name__], 'CARPETA_720P', 'Video_720p')
    else:
        folder_salida = CARPETA_1080P

    ruta_salida_res = os.path.join(carpeta, folder_salida)
    ruta_salida_hechos = os.path.join(carpeta, CARPETA_HECHOS)
    os.makedirs(ruta_salida_res, exist_ok=True)
    os.makedirs(ruta_salida_hechos, exist_ok=True)

    duracion_total_carpeta = sum(d for _, d in videos_4k_reales)

    # --- BUCLE DE VIDEOS INDIVIDUALES ---
    for num_video, (archivo, duracion_total) in enumerate(videos_4k_reales, 1):
        ruta_completa_original = os.path.join(carpeta, archivo)

        if duracion_total <= 0:
            print(f"{Fore.RED}[AVISO CORRUPTO] '{archivo}' tiene una duración de 0.0. Omitiendo...")
            registrar_video_corrupto(carpeta, archivo, "Cabecera rota o archivo dañado")
            continue

        ruta_de_trabajo = asegurar_mkv(ruta_completa_original, carpeta)
        if not ruta_de_trabajo:
            continue

        archivo_trabajo_nombre = os.path.basename(ruta_de_trabajo)
        es_hdr, codec_real = analizar_propiedades_video(ruta_de_trabajo, RUTA_FFPROBE)

        # Empaquetamos los parámetros requeridos (Exactamente 7 elementos)
        params_video = (carpeta, archivo, ruta_de_trabajo, archivo_trabajo_nombre, duracion_total, codec_real, es_hdr)

        params_globales = (
            i_carp,
            carpetas,
            num_video,
            videos_4k_reales,
            total_videos_global_pendientes,
            ruta_salida_res,
            ruta_salida_hechos
        )

        # LLAMADA AL MÓDULO EXTERNO DE PROCESAMIENTO
        procesar_video_individual(params_video, params_globales, gestor_tiempos, config_usuario)

print(f"\n{Fore.CYAN}==================================================")
print(f"{Fore.CYAN}   PROCESO TERMINADO. REVISA EL ARCHIVO DE LOG.   ")
print(f"{Fore.CYAN}==================================================")
logging.info("--- FIN DE LA SESIÓN DE CONVERSIÓN ---")
