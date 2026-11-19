import sys

# Paletas de color disponibles para el sistema
TEMAS = {
    "Oscuro": {
        "FONDO": "#282B31",
        "PANEL": "#35383C",
        "PANEL_2": "#48505B",
        "TEXTO": "#F8FAFC",
        "TEXTO_SEC": "#94A3B8",
        "AZUL": "#38BDF8",
        "VERDE": "#22C55E",
        "AMARILLO": "#F59E0B",
        "ROJO": "#EF4444",
        "MORADO": "#A855F7",
    },
    "Claro": {
        "FONDO": "#F1F5F9",
        "PANEL": "#FFFFFF",
        "PANEL_2": "#E2E8F0",
        "TEXTO": "#0F172A",
        "TEXTO_SEC": "#64748B",
        "AZUL": "#0284C7",
        "VERDE": "#16A34A",
        "AMARILLO": "#D97706",
        "ROJO": "#DC2626",
        "MORADO": "#9333EA",
    },
    "Verde Terrario": {
        "FONDO": "#0C1610",
        "PANEL": "#14261C",
        "PANEL_2": "#1E382A",
        "TEXTO": "#ECFDF5",
        "TEXTO_SEC": "#6EE7B7",
        "AZUL": "#34D399",
        "VERDE": "#22C55E",
        "AMARILLO": "#FBBF24",
        "ROJO": "#F87171",
        "MORADO": "#A78BFA",
    },
    "Nocturno Ámbar": {
        "FONDO": "#14110E",
        "PANEL": "#201A14",
        "PANEL_2": "#322920",
        "TEXTO": "#FEF3C7",
        "TEXTO_SEC": "#FBBF24",
        "AZUL": "#F59E0B",
        "VERDE": "#84CC16",
        "AMARILLO": "#F59E0B",
        "ROJO": "#EF4444",
        "MORADO": "#F43F5E",
    },
}

# Tema activo inicial
TEMA_ACTUAL = "Oscuro"

# Variables globales de color en uso
FONDO = TEMAS[TEMA_ACTUAL]["FONDO"]
PANEL = TEMAS[TEMA_ACTUAL]["PANEL"]
PANEL_2 = TEMAS[TEMA_ACTUAL]["PANEL_2"]
TEXTO = TEMAS[TEMA_ACTUAL]["TEXTO"]
TEXTO_SEC = TEMAS[TEMA_ACTUAL]["TEXTO_SEC"]
AZUL = TEMAS[TEMA_ACTUAL]["AZUL"]
VERDE = TEMAS[TEMA_ACTUAL]["VERDE"]
AMARILLO = TEMAS[TEMA_ACTUAL]["AMARILLO"]
ROJO = TEMAS[TEMA_ACTUAL]["ROJO"]
MORADO = TEMAS[TEMA_ACTUAL]["MORADO"]

# Aplica un nuevo tema y sincroniza las variables en los modulos de la app
def aplicar_tema(nombre_tema):
    global TEMA_ACTUAL, FONDO, PANEL, PANEL_2, TEXTO, TEXTO_SEC, AZUL, VERDE, AMARILLO, ROJO, MORADO
    if nombre_tema not in TEMAS:
        return
    TEMA_ACTUAL = nombre_tema
    paleta = TEMAS[nombre_tema]
    FONDO = paleta["FONDO"]
    PANEL = paleta["PANEL"]
    PANEL_2 = paleta["PANEL_2"]
    TEXTO = paleta["TEXTO"]
    TEXTO_SEC = paleta["TEXTO_SEC"]
    AZUL = paleta["AZUL"]
    VERDE = paleta["VERDE"]
    AMARILLO = paleta["AMARILLO"]
    ROJO = paleta["ROJO"]
    MORADO = paleta["MORADO"]

    # Sincroniza variables en todos los modulos que las usan
    modulos = ["ui.estilos", "ui.sensores", "ui.configuracion", "ui.graficas", "ui.eventos", "__main__"]
    for mod_name in modulos:
        if mod_name in sys.modules:
            mod = sys.modules[mod_name]
            setattr(mod, "TEMA_ACTUAL", nombre_tema)
            for k, v in paleta.items():
                setattr(mod, k, v)
