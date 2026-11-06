import machine
from machine import Pin, ADC, I2C
import dht
from time import sleep
import ssd1306
import network
import urequests

# Configuración de Sensores y Pines
sensor = dht.DHT22(Pin(4))
adc_ldr = ADC(Pin(34))
adc_ldr.atten(ADC.ATTN_11DB)
led = Pin(23, Pin.OUT)

# Configuración pantalla OLED I2C (GPIO 21 SDA, GPIO 22 SCL) 
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
ANCHO = 128
ALTO = 64
oled = ssd1306.SSD1306_I2C(ANCHO, ALTO, i2c)

# Conexión a la red Wi-Fi simulada en Wokwi
ssid = "Wokwi-GUEST"
password = ""

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

print("Conectando a WiFi...", end="")
while not wlan.isconnected():
    print(".", end="")
    sleep(0.5)

print("\n¡Conexión establecida con éxito!")
print("Configuración de red (IP/Subnet/GW/DNS):", wlan.ifconfig())
print("Iniciando lecturas y transmisión por WiFi...\n")

while True:
    # Verificación de reconexión por si se cae la red
    if not wlan.isconnected():
        print("Reconectando a WiFi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            sleep(0.5)

    try:
        # Lectura del DHT22
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        # Lectura del LDR (Luz)
        valor_raw = adc_ldr.read()
        luz_porcentaje = int(((4095 - valor_raw) / 4095) * 100)

        # Control del LED según la temperatura
        if temp > 39:
            estado_temp = "ALTA"
            led.on()
        else:
            estado_temp = "OK"
            led.off()

        #  Actualizar la Pantalla OLED
        oled.fill(0)  # Limpia el buffer de pantalla para evitar texto encimado
        oled.text("TerraPapu", 8, 0)
        oled.hline(0, 12, 128, 1)
        oled.text(f"Temp: {temp} C", 0, 20)
        oled.text(f"Humedad: {hum} %", 0, 32)
        oled.text(f"Luz: {luz_porcentaje} %", 0, 44)
        oled.text(f"Estado: {estado_temp}", 0, 56)
        oled.show()

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
            
        respuesta.close() # Importante: cierra la conexión para liberar memoria RAM

    except Exception as e:
        print(f"Error durante el ciclo: {e}")

    # Pausa de 3 segundos entre cada transmisión
    sleep(3)