import json
from uuid import uuid4

from services.preferencias import RUTA, guardar_json


RUTA_SENSORES = RUTA.with_name("sensores.json")
VISUALIZACIONES = {"grafica": "Gráfica de línea", "circular": "Indicador circular (%)"}


def validar_sensor(nombre, descripcion, pines, visualizacion):
    campos = [
        ("nombre", nombre, 40),
        ("descripción", descripcion, 240),
        ("pines", pines, 80),
    ]
    for etiqueta, valor, maximo in campos:
        if not isinstance(valor, str) or not 1 <= len(valor.strip()) <= maximo:
            raise ValueError(f"Escribe {etiqueta} entre 1 y {maximo} caracteres.")
    if not isinstance(visualizacion, str) or visualizacion not in VISUALIZACIONES:
        raise ValueError("Selecciona cómo se mostrará el sensor.")
    return {
        "nombre": nombre.strip(),
        "descripcion": descripcion.strip(),
        "pines": pines.strip(),
        "visualizacion": visualizacion,
    }


def cargar_sensores():
    try:
        datos = json.loads(RUTA_SENSORES.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(datos, list):
        return []
    sensores = []
    ids = set()
    for dato in datos:
        if not isinstance(dato, dict):
            continue
        identificador = dato.get("id")
        if not isinstance(identificador, str) or not identificador or identificador in ids:
            continue
        try:
            sensor = validar_sensor(
                dato.get("nombre"), dato.get("descripcion"), dato.get("pines"), dato.get("visualizacion")
            )
        except ValueError:
            continue
        ids.add(identificador)
        sensores.append({"id": identificador, **sensor})
    return sensores


def agregar_sensor(sensores, nombre, descripcion, pines, visualizacion):
    sensor = {"id": uuid4().hex, **validar_sensor(nombre, descripcion, pines, visualizacion)}
    guardar_json(RUTA_SENSORES, [*sensores, sensor])
    sensores.append(sensor)
    return sensor


def editar_sensor(sensores, identificador, nombre, descripcion, pines, visualizacion):
    cambios = validar_sensor(nombre, descripcion, pines, visualizacion)
    for indice, sensor in enumerate(sensores):
        if sensor["id"] == identificador:
            nuevo_catalogo = sensores.copy()
            nuevo_catalogo[indice] = {**sensor, **cambios}
            guardar_json(RUTA_SENSORES, nuevo_catalogo)
            sensores[:] = nuevo_catalogo
            return
    raise ValueError("El sensor ya no está en el catálogo.")


def eliminar_sensor(sensores, identificador):
    nuevo_catalogo = [sensor for sensor in sensores if sensor["id"] != identificador]
    if len(nuevo_catalogo) == len(sensores):
        raise ValueError("El sensor ya no está en el catálogo.")
    guardar_json(RUTA_SENSORES, nuevo_catalogo)
    sensores[:] = nuevo_catalogo
