import json
import math
import os
from pathlib import Path
from urllib.parse import urlsplit


ECOSISTEMAS = (
    "Tropical / Selva (Hum: 70-90% | Temp: 24-28°C)",
    "Desértico / Árido (Hum: 15-30% | Temp: 28-36°C)",
    "Templado / Bosque (Hum: 50-70% | Temp: 20-25°C)",
    "Personalizado",
)
PREDETERMINADAS = {
    "nombre": "Terrario Papu #1",
    "ecosistema": ECOSISTEMAS[0],
    "tema": "Oscuro",
    "notificaciones": True,
    "sonido_termico": False,
    "sonido_desconexion": False,
    "csv_automatico": False,
    "umbral": 39.0,
    "intervalo": 3,
    "url": "http://0.0.0.0:8000/datos",
}
RUTA = Path(os.environ.get("LOCALAPPDATA") or Path.home() / ".config") / "TerraPapu" / "configuracion.json"


def validar_preferencias(datos):
    nombre = str(datos["nombre"]).strip()
    if not 1 <= len(nombre) <= 60:
        raise ValueError("El nombre debe tener entre 1 y 60 caracteres.")
    try:
        umbral = float(str(datos["umbral"]).replace(",", "."))
    except ValueError:
        raise ValueError("Escribe un umbral numérico.") from None
    if not math.isfinite(umbral) or not -40 <= umbral <= 80:
        raise ValueError("El umbral debe estar entre -40 y 80 °C.")
    try:
        intervalo = int(str(datos["intervalo"]))
    except ValueError:
        raise ValueError("Escribe un intervalo en segundos enteros.") from None
    if not 1 <= intervalo <= 3600:
        raise ValueError("El intervalo debe estar entre 1 y 3600 segundos.")
    url = str(datos["url"]).strip()
    try:
        partes = urlsplit(url)
        if (
            partes.scheme not in ("http", "https")
            or not partes.hostname
            or partes.username is not None
            or partes.fragment
            or any(c.isspace() for c in url)
            or partes.port == 0
        ):
            raise ValueError
    except ValueError:
        raise ValueError("Escribe una URL HTTP o HTTPS válida, sin credenciales.") from None
    if datos["ecosistema"] not in ECOSISTEMAS or datos["tema"] not in (
        "Oscuro", "Claro", "Verde Terrario", "Nocturno Ámbar"
    ):
        raise ValueError("Selecciona un ecosistema y un tema disponibles.")
    for clave in ("notificaciones", "sonido_termico", "sonido_desconexion", "csv_automatico"):
        if not isinstance(datos[clave], bool):
            raise ValueError("Los interruptores deben ser valores booleanos.")
    return {**datos, "nombre": nombre, "umbral": umbral, "intervalo": intervalo, "url": url}


def cargar_preferencias():
    try:
        datos = json.loads(RUTA.read_text(encoding="utf-8"))
        if isinstance(datos, dict):
            return validar_preferencias({
                clave: datos.get(clave, valor) for clave, valor in PREDETERMINADAS.items()
            })
    except (OSError, ValueError):
        pass
    return PREDETERMINADAS.copy()


def guardar_preferencias(datos):
    guardar_json(RUTA, datos)


def guardar_json(ruta, datos):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(".tmp")
    temporal.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    temporal.replace(ruta)
