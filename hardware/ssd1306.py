from time import sleep
from config import Dispositivos
from config_wifi import RedWiFi

class SistemaTransmision:
    def __init__(self):
        # Conexión a la red Wi-Fi simulada en Wokwi
        self.ssid = "Wokwi-GUEST"
        self.password = ""

        self.red = RedWiFi(self.ssid, self.password)
        self.hw = Dispositivos()

    def ejecutar(self):
        self.red.conectar()

        while True:
            self.red.verificar_conexion()

            try:
                temp, hum, luz_porcentaje, estado_temp = self.hw.leer_sensores()
                self.hw.actualizar_pantalla(temp, hum, luz_porcentaje, estado_temp)
                self.hw.enviar_datos(temp, hum, luz_porcentaje, estado_temp)

            except Exception as e:
                print(f"Error durante el ciclo: {e}")

            # Pausa de 3 segundos entre cada transmisión
            sleep(3)

if __name__ == "__main__":
    sistema = SistemaTransmision()
    sistema.ejecutar()