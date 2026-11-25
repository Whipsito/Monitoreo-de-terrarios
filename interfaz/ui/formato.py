def formatear_medicion(valor):
    """Presenta un número con un decimal como máximo."""
    texto = f"{valor:.1f}".removesuffix(".0")
    return "0" if texto == "-0" else texto
