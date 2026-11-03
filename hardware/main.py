import machine
from machine import Pin
import dht
from time import sleep

# Configurar el pin GPIO 4 para el sensor DHT22
sensor = dht.DHT22(Pin(4))
adc_ldr = machine.ADC(Pin(34))
adc_ldr.atten(machine.ADC.ATTN_11DB)
led = Pin(23, Pin.OUT)

print("Iniciando lecturas del sensor DHT22...")

while True:
    try:
        # Realizar la medición
        sensor.measure()
        
        # Leer los valores medidos
        temp = sensor.temperature()   # Temperatura en °C
        hum = sensor.humidity()       # Humedad relativa en %
        
        # Mostrar los resultados por consola
        print(f"Temperatura: {temp:.1f} °C  |  Humedad: {hum:.1f} %")
        
        
    except OSError as e:
        print("Error al leer el sensor DHT22:", e)

    valor_raw = adc_ldr.read()
    luz_porcentaje = int(((4095 - valor_raw) / 4095) * 100)
    
    print(f"ADC Raw: {valor_raw} | Porcentaje de Luz: {luz_porcentaje}%")
    sleep(0.5)
    if temp > 39:
        print ("Temperatura alta")
        led.on()
    else:
        print ("Temperatura estable")
    # Esperar 2 segundos antes de la siguiente lectura (frecuencia recomendada)
    sleep(2)