import network
from time import sleep

class RedWiFi:
    def __init__(self, ssid="Wokwi-GUEST", password=""):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)

    def conectar(self):
        self.wlan.active(True)
        self.wlan.connect(self.ssid, self.password)

        print("Conectando a WiFi...", end="")
        while not self.wlan.isconnected():
            print(".", end="")
            sleep(0.5)

        print("\n¡Conexión establecida con éxito!")
        print("Configuración de red (IP/Subnet/GW/DNS):", self.wlan.ifconfig())
        print("Iniciando lecturas y transmisión por WiFi...\n")

    def verificar_conexion(self):
        # Verificación de reconexión por si se cae la red
        if not self.wlan.isconnected():
            print("Reconectando a WiFi...")
            self.wlan.connect(self.ssid, self.password)
            while not self.wlan.isconnected():
                sleep(0.5)