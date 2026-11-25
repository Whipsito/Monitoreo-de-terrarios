from machine import Pin, ADC, I2C
import dht
import ssd1306

class Dispositivos:
    def __init__(self):
        # Configuración de Sensores y Pines
        self.sensor = dht.DHT22(Pin(4))
        self.adc_ldr = ADC(Pin(34))
        self.adc_ldr.atten(ADC.ATTN_11DB)
        self.led = Pin(23, Pin.OUT, value=0)

        # Configuración pantalla OLED I2C (GPIO 21 SDA, GPIO 22 SCL)
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21))
        self.ANCHO = 128
        self.ALTO = 64
        try:
            self.oled = ssd1306.SSD1306_I2C(self.ANCHO, self.ALTO, self.i2c)
        except OSError as error:
            self.oled = None
            print("OLED no disponible:", error)

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
        if self.oled is None:
            return
        # Actualizar la Pantalla OLED
        self.oled.fill(0)  # Limpia el buffer de pantalla para evitar texto encimado
        self.oled.text("TerraPapu", 8, 0)
        self.oled.hline(0, 12, 128, 1)
        self.oled.text(f"Temp: {temp} C", 0, 20)
        self.oled.text(f"Humedad: {hum} %", 0, 32)
        self.oled.text(f"Luz: {luz_porcentaje} %", 0, 44)
        self.oled.text(f"Estado: {estado_temp}", 0, 56)
        self.oled.show()
