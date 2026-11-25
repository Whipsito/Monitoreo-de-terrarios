import csv
from datetime import datetime
from pathlib import Path


class RegistroEventos:
    """Mantiene las lecturas recientes y permite guardarlas en un CSV."""

    def __init__(self, limite=1000):
        self.eventos = []
        self.limite = limite

    def agregar_lectura(self, lectura, prueba=False, origen="simulacion"):
        evento = {
            "hora": datetime.now().strftime("%H:%M:%S"),
            "temperatura": lectura["temperatura"],
            "humedad": lectura["humedad"],
            "luz": lectura["luz"],
            "led": lectura["led"],
            "origen": "prueba termica" if prueba else origen,
        }
        self.eventos.insert(0, evento)
        self.eventos = self.eventos[: self.limite]
        return evento

    def obtener_recientes(self, cantidad=20):
        return self.eventos[:cantidad]

    def limpiar(self):
        self.eventos.clear()

    def exportar_csv(self):
        marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        nombre_archivo = f"registro_eventos_{marca_tiempo}.csv"
        ruta = Path(__file__).resolve().parents[2] / "exports" / nombre_archivo
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with ruta.open("w", newline="", encoding="utf-8") as archivo:
            campos = ["hora", "temperatura", "humedad", "luz", "led", "origen"]
            escritor = csv.DictWriter(archivo, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(reversed(self.eventos))
        return ruta
