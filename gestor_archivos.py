import os
from colorama import Fore
from metadatos import extraer_metadatos
from configuracion import CARPETA_1080P, CARPETA_HECHOS

def escanear_cola_global(carpetas, ruta_ffprobe):
    """
    Escanea todas las carpetas del TXT.
    Calcula la duración global total, cuenta los videos pendientes
    y genera el diccionario estructurado de datos.
    """
    print(f"{Fore.WHITE}Escaneando carpetas cargadas para calcular tiempos totales...")
    extensiones = ('.mp4', '.mkv', '.mov', '.avi', '.flv', '.webm')
    duracion_total_global = 0.0
    total_videos_global_pendientes = 0
    datos_carpetas = {}

    for carp in carpetas:
        if os.path.exists(carp):
            archs_filtrados = []

            # Leemos todos los archivos de la carpeta
            for a in os.listdir(carp):
                # Pasamos el nombre a minúsculas solo para comparar extensiones y etiquetas de forma segura
                nombre_minusculas = a.lower()

                if nombre_minusculas.endswith(extensiones):
                    # Evitamos leer los videos temporales en curso o los que ya están guardados en la carpeta final
                    if "temp_" in nombre_minusculas or CARPETA_1080P.lower() in nombre_minusculas:
                        continue

                    # Filtro inteligente de nombres: Buscamos cualquier rastro de que sea un video de alta definición (4k, 2160p, 2160P)
                    # Eliminamos el filtro rígido que descartaba los "x264" para que ffprobe decida de verdad si es 4K o no
                    if "2160p" in nombre_minusculas or "4k" in nombre_minusculas:
                        # Descartamos si el nombre dice explícitamente "1080p" o "1080" para no re-procesar copias viejas
                        if "1080" not in nombre_minusculas:
                            archs_filtrados.append(a)

            duraciones_carp = []
            for arch in archs_filtrados:
                d, _, _ = extraer_metadatos(os.path.join(carp, arch), ruta_ffprobe)
                if d > 0:
                    duraciones_carp.append((arch, d))
                    duracion_total_global += d
                    total_videos_global_pendientes += 1
            datos_carpetas[carp] = duraciones_carp

    print(f"{Fore.GREEN}[OK] Cola lista. {len(carpetas)} carpetas. {total_videos_global_pendientes} videos 4K detectados.\n")
    return duracion_total_global, total_videos_global_pendientes, datos_carpetas


def finalizar_almacenamiento_video(carpeta, archivo, ruta_temporal, ruta_destino_final, ruta_completa_original, ruta_original_hechos):
    """
    Se encarga de mover el archivo final procesado a la carpeta 1080p
    y trasladar el original 4K a la carpeta de HECHOS.
    """
    print(f"{Fore.CYAN}Paso 2/3: Almacenando archivo final procesado...")

    # Verificación extra por seguridad: si el archivo de destino final ya existe, lo quitamos para evitar bloqueos de Windows
    if os.path.exists(ruta_destino_final):
        os.remove(ruta_destino_final)

    os.replace(ruta_temporal, ruta_destino_final)

    print(f"{Fore.CYAN}Paso 3/3: Trasladando video 4K original a '{CARPETA_HECHOS}'...")

    # Verificación extra para el traslado a HECHOS
    if os.path.exists(ruta_original_hechos):
        os.remove(ruta_original_hechos)

    os.rename(ruta_completa_original, ruta_original_hechos)

    print(f"{Fore.GREEN}[ÉXITO] El video se ha procesado y guardado correctamente.\n")
