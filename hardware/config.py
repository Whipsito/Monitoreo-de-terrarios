import machine
from machine import Pin, ADC, I2C
import dht
import ssd1306
import urequests

class Dispositivos:
    def __init__(self):
        # Configuración de Sensores y Pines
        self.sensor = dht.DHT22(Pin(4))
        self.adc_ldr = ADC(Pin(34))
        self.adc_ldr.atten(ADC.ATTN_11DB)
        self.led = Pin(23, Pin.OUT)

        # Configuración pantalla OLED I2C (GPIO 21 SDA, GPIO 22 SCL)
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21))
        self.ANCHO = 128
        self.ALTO = 64
        self.oled = ssd1306.SSD1306_I2C(self.ANCHO, self.ALTO, self.i2c)

    def leer_sensores(self):
        # Lectura del DHT22
        self.sensor.measure()
        temp = self.sensor.temperature()
        hum = self.sensor.humidity()

        # Lectura del LDR (Luz)
        valor_raw = self.adc_ldr.read()
        luz_porcentaje = int(((4095 - valor_raw) / 4095) * 100)

        # Control del LED según la temperatura
        if temp > 39:
            estado_temp = "ALTA"
            self.led.on()
        else:
            estado_temp = "OK"
            self.led.off()

        return temp, hum, luz_porcentaje, estado_temp

    def actualizar_pantalla(self, temp, hum, luz_porcentaje, estado_temp):
        # Actualizar la Pantalla OLED
        self.oled.fill(0)  # Limpia el buffer de pantalla para evitar texto encimado
        self.oled.text("TerraPapu", 8, 0)
        self.oled.hline(0, 12, 128, 1)
        self.oled.text(f"Temp: {temp} C", 0, 20)
        self.oled.text(f"Humedad: {hum} %", 0, 32)
        self.oled.text(f"Luz: {luz_porcentaje} %", 0, 44)
        self.oled.text(f"Estado: {estado_temp}", 0, 56)
        self.oled.show()

    def enviar_datos(self, temp, hum, luz_porcentaje, estado_temp):
        # Envío de datos por WiFi (HTTP POST)
        payload = {
            "temperatura": temp,
            "humedad": hum,
            "luz": luz_porcentaje,
            "led": estado_temp
        }

        # API de prueba que procesa y devuelve los mismos datos enviados
        url = "http://httpbin.org/post"
        headers = {'Content-Type': 'application/json'}

        print("Enviando paquete de datos vía Wi-Fi...")
        respuesta = urequests.post(url, json=payload, headers=headers)

        if respuesta.status_code == 200:
            print(f"[WiFi TX OK] Código de servidor: {respuesta.status_code}")
            print("Payload enviado:", payload)
        else:
            print(f"[WiFi Error] Código de estado: {respuesta.status_code}")

        respuesta.close()  # Importante: cierra la conexión para liberar memoria RAM