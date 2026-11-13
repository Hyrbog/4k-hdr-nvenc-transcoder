import os
import sys
import shutil
import logging
from datetime import datetime
from colorama import Fore
from interfaz import limpiar_pantalla

# ==========================================
#          CONFIGURACIÓN DE RUTAS
# ==========================================
RUTA_FFMPEG = shutil.which("ffmpeg") or r"C:\Tools\ffmpeg\bin\ffmpeg.exe"
RUTA_FFPROBE = shutil.which("ffprobe") or r"C:\Tools\ffmpeg\bin\ffprobe.exe"
ARCHIVO_TXT = os.path.join(os.path.dirname(__file__), "carpetas.txt")

# Carpetas de salida dinámicas según resolución elegida
CARPETA_4K = "PROCESADOS A 4K"
CARPETA_1080P = "CONVERTIDOS A 1080p"
CARPETA_720P = "CONVERTIDOS A 720p"
CARPETA_HECHOS = "!!! - HECHOS"

ARCHIVO_LOG = os.path.join(os.path.dirname(__file__), "log_conversion.txt")
ARCHIVO_CORRUPTOS = os.path.join(os.path.dirname(__file__), "videos_corruptos.txt")

# ==========================================
#          SISTEMA DE LOGGING
# ==========================================
logging.basicConfig(
    filename=ARCHIVO_LOG, level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8'
)

def registrar_video_corrupto(carpeta, archivo, razon, codigo_error=None):
    """Guarda los datos del archivo fallido en el TXT independiente."""
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg_err = f" | Código FFmpeg: {codigo_error}" if codigo_error is not None else ""
    linea = f"[{ahora}] CARPETA: {carpeta} | ARCHIVO: {archivo} | ERROR: {razon}{msg_err}\n"
    with open(ARCHIVO_CORRUPTOS, 'a', encoding='utf-8') as f:
        f.write(linea)

# ==========================================
#       INTERFAZ DE SELECCIÓN DE BITRATE
# ==========================================
def solicitar_bitrate():
    """Muestra el menú interactivo con validación de entrada numérica."""
    limpiar_pantalla()
    print(f"{Fore.CYAN}==================================================")
    print(f"{Fore.CYAN}          CONFIGURACIÓN DE CALIDAD DE VIDEO       ")
    print(f"{Fore.CYAN}==================================================")
    print(f"{Fore.WHITE}1) Alta Calidad (15000 kbps)")
    print(f"{Fore.WHITE}2) Calidad Estándar (10000 kbps) [Recomendado]")
    print(f"{Fore.WHITE}3) Calidad Ligera (6000 kbps)")
    print(f"{Fore.WHITE}4) Personalizado (Introducir valor manual)")
    print(f"{Fore.WHITE}5) Mantener bitrate original (Aproximado)")
    print(f"{Fore.CYAN}==================================================")

    while True:
        opcion = input(f"{Fore.YELLOW}Selecciona una opción (1-5): ").strip()
        if opcion == "1":
            return "15000k"
        elif opcion == "2":
            return "10000k"
        elif opcion == "3":
            return "6000k"
        elif opcion == "4":
            print(f"\n{Fore.WHITE}-> Introduce un valor numérico entre {Fore.GREEN}2000{Fore.WHITE} y {Fore.GREEN}40000{Fore.WHITE} (en kbps).")
            while True:
                valor = input(f"{Fore.YELLOW}Bitrate personalizado: ").strip()
                if valor.isdigit():
                    num = int(valor)
                    if 2000 <= num <= 40000:
                        return f"{num}k"
                    else:
                        print(f"{Fore.RED}[ERROR] El valor debe estar estrictamente entre 2000 y 40000.")
                else:
                    print(f"{Fore.RED}[ERROR] Entrada no válida. Introduce solo números sin letras.")
        elif opcion == "5":
            return "original"
        else:
            print(f"{Fore.RED}[ERROR] Opción incorrecta. Selecciona del 1 al 5.")
