import http.client
import json
from urllib.parse import urlsplit


def recibir_lectura(url):
    """Devuelve una lectura validada, o None si la placa aún no tiene datos."""
    destino = urlsplit(url)
    tipo = http.client.HTTPSConnection if destino.scheme == "https" else http.client.HTTPConnection
    conexion = tipo(destino.hostname, destino.port, timeout=2)
    try:
        ruta = destino.path or "/datos"
        if destino.query:
            ruta += "?" + destino.query
        conexion.request("GET", ruta, headers={"Accept": "application/json"})
        respuesta = conexion.getresponse()
        if respuesta.status == 503:
            return None
        if respuesta.status != 200:
            raise ValueError(f"El ESP32 respondió con HTTP {respuesta.status}.")
        cuerpo = respuesta.read(2049)
        if len(cuerpo) > 2048:
            raise ValueError("La respuesta del ESP32 supera el tamaño esperado.")
        lectura = json.loads(cuerpo)
    finally:
        conexion.close()

    if not isinstance(lectura, dict):
        raise ValueError("Se esperaba un objeto JSON.")
    rangos = {"temperatura": (-40, 80), "humedad": (0, 100), "luz": (0, 100)}
    for campo, (minimo, maximo) in rangos.items():
        valor = lectura.get(campo)
        if type(valor) not in (float, int) or not minimo <= valor <= maximo:
            raise ValueError(f"Valor inválido para {campo}.")
    if lectura.get("led") not in ("OK", "ALTA"):
        raise ValueError("Estado del LED inválido.")
    identificador = lectura.get("id_lectura")
    if not isinstance(identificador, str) or not 1 <= len(identificador) <= 64:
        raise ValueError("Falta el identificador de la lectura.")
    return lectura
