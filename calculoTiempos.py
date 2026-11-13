import time

class CronometroVideo:
    def __init__(self):
        self.inicio = None

    def iniciar(self):
        """Registra el momento exacto en que empieza la conversión."""
        self.inicio = time.time()

    def obtener_tiempo_transcurrido(self):
        """Calcula el tiempo total desde el inicio y lo devuelve en hh:mm:ss."""
        if not self.inicio:
            return "00:00:00"

        segundos_totales = int(time.time() - self.inicio)
        horas = segundos_totales // 3600
        minutos = (segundos_totales % 3600) // 60
        segundos = segundos_totales % 60

        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    def finalizar_tiempos(self):
        """Devuelve el tiempo restante a cero y el tiempo transcurrido final."""
        restante = "00:00:00"
        transcurrido = self.obtener_tiempo_transcurrido()
        return restante, transcurrido


class GestorTiempos:
    def __init__(self, duracion_global):
        self.duracion_total_global = duracion_global
        self.segundos_ya_procesados_global = 0.0
        self.inicio_video_actual = None

    def iniciar_reloj_video(self):
        """Registra el inicio de la conversión del video actual."""
        self.inicio_video_actual = time.time()

    def calcular_etas(self, segundos_convertidos, duracion_video, duracion_carpeta, ya_procesados_carpeta, velocidad_media):
        """Calcula el paquete de tiempos restantes (ETA) actuales."""
        segundos_restantes_video = max(0.0, duracion_video - segundos_convertidos)
        eta_video = segundos_restantes_video / velocidad_media

        segundos_restantes_carpeta = max(0.0, duracion_carpeta - (ya_procesados_carpeta + segundos_convertidos))
        eta_carpeta = segundos_restantes_carpeta / velocidad_media

        segundos_restantes_global = max(0.0, self.duracion_total_global - (self.segundos_ya_procesados_global + segundos_convertidos))
        eta_global = segundos_restantes_global / velocidad_media

        return eta_video, eta_carpeta, eta_global

    def finalizar_video(self, duracion_video, v_tot_carp, v_tot_glob):
        """Fuerza los ETAs a cero manteniendo los contadores de videos en la tupla."""
        paquete_ceros = (0.0, 0.0, 0.0, v_tot_carp, v_tot_glob)

        tiempo_transcurrido = "00:00:00"
        if self.inicio_video_actual:
            segundos_totales = int(time.time() - self.inicio_video_actual)
            horas = segundos_totales // 3600
            minutos = (segundos_totales % 3600) // 60
            segundos = segundos_totales % 60
            tiempo_transcurrido = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

        self.segundos_ya_procesados_global += duracion_video

        return paquete_ceros, tiempo_transcurrido
