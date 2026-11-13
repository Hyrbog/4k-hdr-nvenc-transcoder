import os
import sys
from colorama import Fore

def limpiar_pantalla():
    """Limpia la consola según el sistema operativo."""
    os.system('cls' if os.name == 'nt' else 'clear')

def parsear_tiempo(tiempo_str):
    """Convierte un string HH:MM:SS.mm en segundos totales."""
    try:
        partes = tiempo_str.split(':')
        h = float(partes[0])
        m = float(partes[1])
        s = float(partes[2])
        return (h * 3600) + (m * 60) + s
    except:
        return 0.0

def formatear_segundos(segundos):
    """Convierte segundos en formato legible HH:MM:SS."""
    if isinstance(segundos, str):
        return segundos  # Si ya viene formateado como texto desde el corrector, lo deja pasar
    if segundos < 0 or segundos is None:
        return "00:00:00"
    h = int(segundos) // 3600
    m = (int(segundos) % 3600) // 60
    s = int(segundos) % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def mostrar_barra_progreso(actual, total, fps, velocidad, ticks_restantes=None, forzar_100=False):
    """Dibuja la barra de progreso en tiempo real y gestiona las 3 líneas fijas de ETA inferiores."""
    if total <= 0:
        return

    if forzar_100:
        porcentaje = 100
        actual = total
    else:
        porcentaje = min(100, int((actual / total) * 100))

    longitud_barra = 40
    bloques = int((porcentaje / 100) * longitud_barra)

    barra = f"{Fore.GREEN}█" * bloques + f"{Fore.WHITE}░" * (longitud_barra - bloques)

    txt_actual = formatear_segundos(actual)
    txt_total = formatear_segundos(total)

    # \r vuelve al inicio de la línea.
    sys.stdout.write(
        f"\r{Fore.CYAN}[{barra}{Fore.CYAN}] {Fore.YELLOW}{porcentaje}% "
        f"{Fore.WHITE}({txt_actual}/{txt_total}) "
        f"{Fore.MAGENTA}{fps} fps {Fore.BLUE}[{velocidad}]     "
    )
    sys.stdout.flush()

    # Si se pasan los datos de tiempo restante (ETA), los pintamos en líneas inferiores fijas
    if ticks_restantes:
        eta_vid, eta_carp, eta_glob, v_tot_carp, v_tot_glob = ticks_restantes

        # Línea 1: Vídeo actual
        txt_l1 = f"{Fore.GREEN}{formatear_segundos(eta_vid)}" if eta_vid is not None else f"{Fore.LIGHTBLACK_EX}Calculando..."

        # Línea 2: Carpeta actual
        if v_tot_carp <= 1:
            txt_l2 = f"{Fore.LIGHTBLACK_EX}Solo se está procesando un archivo en esta carpeta."
        elif eta_carp is not None:
            txt_l2 = f"{Fore.GREEN}{formatear_segundos(eta_carp)}"
        else:
            txt_l2 = f"{Fore.LIGHTBLACK_EX}Calculando..."

        # Línea 3: Cola global
        if v_tot_glob <= 1:
            txt_l3 = f"{Fore.LIGHTBLACK_EX}Solo se está procesando una carpeta/archivo en total."
        elif eta_glob is not None:
            txt_l3 = f"{Fore.GREEN}{formatear_segundos(eta_glob)}"
        else:
            txt_l3 = f"{Fore.LIGHTBLACK_EX}Calculando..."

        # Saltamos líneas, escribimos limpiando la línea entera con códigos ANSI y volvemos arriba
        sys.stdout.write(
            f"\n\033[K{Fore.WHITE}• Tiempo restante del video en curso: {txt_l1}"
            f"\n\033[K{Fore.WHITE}• Tiempo restante de toda la carpeta en curso: {txt_l2}"
            f"\n\033[K{Fore.WHITE}• Tiempo restante para procesar todas las carpetas: {txt_l3}"
        )

        if forzar_100:
            # CORRECCIÓN DE POSICIÓN: Si terminó, dejamos el cursor abajo del todo de forma definitiva
            sys.stdout.write("\n")
        else:
            # Si sigue procesando, sube 3 líneas para redibujar en la siguiente vuelta
            sys.stdout.write("\033[3A")

        sys.stdout.flush()

def limpiar_lineas_eta():
    """Limpia las tres líneas de texto inferiores al terminar un vídeo."""
    sys.stdout.write("\n\033[K\n\033[K\n\033[K\033[3A")
    sys.stdout.flush()

def mostrar_aviso_remux(nombre_archivo, carpeta_destino):
    """Informa al usuario de que un archivo MP4 se está pasando a la estructura MKV."""
    print(f"\n{Fore.YELLOW}  [AVISO CONTENEDOR] '{nombre_archivo}' es un archivo MP4.")
    print(f"{Fore.GREEN}  -> Encapsulando en MKV sin pérdida dentro de: '{os.path.basename(carpeta_destino)}'...")
