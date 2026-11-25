import asyncio
import json
from time import ticks_diff, ticks_ms


class ServidorLecturas:
    def __init__(self, ip):
        self.ip = ip
        self.ultima = None
        self.hora_ultima = None

    async def iniciar(self):
        self.servidor = await asyncio.start_server(self.responder, self.ip, 80, backlog=3)

    def publicar(self, lectura):
        self.ultima = json.dumps(lectura).encode()
        self.hora_ultima = ticks_ms()

    async def leer_cabeceras(self, reader):
        datos = b""
        while b"\r\n\r\n" not in datos and len(datos) < 2048:
            bloque = await reader.read(min(256, 2048 - len(datos)))
            if not bloque:
                break
            datos += bloque
        if b"\r\n\r\n" not in datos:
            return ()
        return datos.split(b"\r\n", 1)[0].split()

    async def responder(self, reader, writer):
        try:
            peticion = await asyncio.wait_for_ms(self.leer_cabeceras(reader), 1000)
            if len(peticion) != 3:
                estado, cuerpo = "400 Bad Request", b'{"error":"peticion incompleta"}'
            elif peticion[0] != b"GET":
                estado, cuerpo = "405 Method Not Allowed", b'{"error":"usa GET"}'
            elif peticion[1] != b"/datos":
                estado, cuerpo = "404 Not Found", b'{"error":"ruta no disponible"}'
            elif self.ultima is None or ticks_diff(ticks_ms(), self.hora_ultima) > 10000:
                estado, cuerpo = "503 Service Unavailable", b'{"error":"sin lecturas recientes"}'
            else:
                estado, cuerpo = "200 OK", self.ultima
            cabecera = (
                "HTTP/1.1 {}\r\nContent-Type: application/json\r\n"
                "Content-Length: {}\r\nCache-Control: no-store\r\n"
                "Connection: close\r\n\r\n"
            ).format(estado, len(cuerpo))
            writer.write(cabecera.encode() + cuerpo)
            await asyncio.wait_for_ms(writer.drain(), 1000)
        except (OSError, asyncio.TimeoutError):
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass
