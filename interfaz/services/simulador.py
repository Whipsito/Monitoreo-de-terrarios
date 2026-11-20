import random


# Rangos orientativos para generar lecturas plausibles por ecosistema.
RANGOS_ECOSISTEMA = {
    "tropical": {
        "temperatura": (24.0, 28.0),
        "humedad": (70.0, 90.0),
        "luz": (40, 80),
    },
    "desértico": {
        "temperatura": (28.0, 36.0),
        "humedad": (15.0, 30.0),
        "luz": (70, 100),
    },
    "templado": {
        "temperatura": (20.0, 25.0),
        "humedad": (50.0, 70.0),
        "luz": (30, 70),
    },
    "personalizado": {
        "temperatura": (22.0, 30.0),
        "humedad": (40.0, 70.0),
        "luz": (30, 80),
    },
}


def generar_lectura_simulada(ecosistema, lectura_anterior=None):
    """Genera una lectura estable dentro de los rangos del ecosistema elegido."""
    nombre = ecosistema.lower()
    perfil = next(
        (rangos for clave, rangos in RANGOS_ECOSISTEMA.items() if clave in nombre),
        RANGOS_ECOSISTEMA["personalizado"],
    )

    def siguiente_valor(metrica, variacion):
        minimo, maximo = perfil[metrica]
        anterior = (lectura_anterior or {}).get(metrica)
        if anterior is None:
            return random.uniform(minimo, maximo)
        return max(minimo, min(maximo, anterior + random.uniform(-variacion, variacion)))

    temperatura = round(siguiente_valor("temperatura", 0.4), 1)
    humedad = round(siguiente_valor("humedad", 2.0), 1)
    luz = round(siguiente_valor("luz", 5.0))

    return {
        "temperatura": temperatura,
        "humedad": humedad,
        "luz": luz,
        "led": "ALTA" if temperatura > 39.0 else "OK",
    }
