from colorama import Fore
from configuracion import solicitar_bitrate

def solicitar_configuracion_video():
    """
    Gestiona los menús interactivos iniciales de Bitrate, Resolución y Color.
    """
    # 1. SOLICITAR BITRATE
    # La función solicitar_bitrate() en configuracion.py ahora debe admitir la opción 5
    # y validar un rango numérico de personalizado de hasta 40000.
    bitrate_elegido = solicitar_bitrate()

    # 2. SOLICITAR RESOLUCIÓN
    print(f"{Fore.CYAN}==================================================")
    print(f"{Fore.CYAN}          CONFIGURACIÓN DE LA RESOLUCIÓN          ")
    print(f"{Fore.CYAN}==================================================")
    print(f"{Fore.WHITE}1) 4K (Mantener original)")
    print(f"{Fore.WHITE}2) 1080p")
    print(f"{Fore.WHITE}3) 720p")
    print(f"{Fore.CYAN}==================================================")

    opc_res = input("Seleccione la resolución de salida: ").strip()
    if opc_res == "1":
        resolucion_elegida = "4k"
    elif opc_res == "3":
        resolucion_elegida = "720p"
    else:
        resolucion_elegida = "1080p"  # Por defecto

    # 3. CONFIGURACIÓN DEL MENÚ HDR CONDICIONAL
    print(f"{Fore.CYAN}==================================================")
    print(f"{Fore.CYAN}          CONFIGURACIÓN DEL COLOR                 ")
    print(f"{Fore.CYAN}==================================================")
    print(f"{Fore.WHITE}1) Corregir color a BT.709 (Mapeo de tonos a SDR)")
    print(f"{Fore.WHITE}2) Dejarlo como está (Mantener HDR original)     ")
    print(f"{Fore.CYAN}==================================================")

    opc_hdr = input("En caso de encontrar videos en HDR: ").strip()
    config_corregir_hdr = True if opc_hdr == "1" else False

    return bitrate_elegido, resolucion_elegida, config_corregir_hdr
