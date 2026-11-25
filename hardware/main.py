import asyncio
from binascii import hexlify
from os import urandom
from time import ticks_add, ticks_diff, ticks_ms

from config import Dispositivos
from config_wifi import SSID, iniciar_red
from servidor_http import ServidorLecturas


async def ejecutar():
    red = iniciar_red()
    ip = red.ifconfig()[0]
    servidor = ServidorLecturas(ip)
    await servidor.iniciar()
    print("Red Wi-Fi:", SSID)
    print("Lecturas: http://" + ip + "/datos")

    hardware = Dispositivos()
    arranque = hexlify(urandom(8)).decode()
    numero = 0
    while True:
        siguiente = ticks_add(ticks_ms(), 3000)
        try:
            temp, humedad, luz, led = hardware.leer_sensores()
        except OSError as error:
            print("No se pudo leer el sensor:", error)
        else:
            numero += 1
            servidor.publicar({
                "temperatura": temp,
                "humedad": humedad,
                "luz": luz,
                "led": led,
                "id_lectura": "{}-{}".format(arranque, numero),
            })
            try:
                hardware.actualizar_pantalla(temp, humedad, luz, led)
            except OSError as error:
                print("Error al actualizar OLED:", error)
        await asyncio.sleep_ms(max(1, ticks_diff(siguiente, ticks_ms())))


if __name__ == "__main__":
    asyncio.run(ejecutar())
