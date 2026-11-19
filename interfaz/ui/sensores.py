import flet as ft
from ui.estilos import *

# Fila para una linea de especificacion tecnica
def crear_item_especificacion(etiqueta, valor):
    return ft.Row(
        controls=[
            ft.Text(f"• {etiqueta}:", size=13, color=TEXTO_SEC),
            ft.Text(valor, size=13, weight=ft.FontWeight.W_500, color=TEXTO),
        ],
        spacing=6,
    )

# Construye una ficha tecnica individual para un componente de hardware
def crear_ficha_hardware(titulo, estado_texto, estado_color, pin_texto, especificaciones, icono, icono_color):
    
    # Cabecera con icono, titulo y chip de estado
    cabecera = ft.Row(
        controls=[
            ft.Row(
                controls=[
                    ft.Icon(icono, size=22, color=icono_color),
                    ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD, color=TEXTO),
                ],
                spacing=8,
            ),
            # Chip con el estado operativo
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CIRCLE, size=8, color=estado_color),
                        ft.Text(estado_texto, size=11, weight=ft.FontWeight.BOLD, color=estado_color),
                    ],
                    spacing=6,
                ),
                bgcolor=PANEL_2,
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                border_radius=12,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # Informacion del pin asignado en el ESP32
    info_pin = ft.Row(
        controls=[
            ft.Text("Pin ESP32:", size=13, color=TEXTO_SEC),
            ft.Text(pin_texto, size=13, weight=ft.FontWeight.BOLD, color=AZUL),
        ],
        spacing=6,
    )

    # Lineas de especificaciones tecnicas
    filas_specs = [crear_item_especificacion(item[0], item[1]) for item in especificaciones]

    # Contenedor final de la ficha tecnica que se expande verticalmente
    return ft.Container(
        content=ft.Column(
            controls=[
                cabecera,
                info_pin,
                ft.Divider(color=PANEL_2, height=1),
                ft.Column(controls=filas_specs, spacing=8, expand=True),
            ],
            spacing=10,
            expand=True,
        ),
        bgcolor=PANEL,
        padding=20,
        border_radius=12,
        expand=True,
    )

# Genera la vista completa de diagnostico de hardware ocupando toda la pantalla
def crear_vista_sensores():
    
    # Ficha del Sensor DHT22
    ficha_dht22 = crear_ficha_hardware(
        titulo="SENSOR DHT22",
        estado_texto="OPERATIVO",
        estado_color=VERDE,
        pin_texto="GPIO 4 (Digital)",
        especificaciones=[
            ("Rango Temp", "-40 °C a 80 °C"),
            ("Precisión T", "±0.5 °C"),
            ("Rango Hum", "0% a 100% HR"),
            ("Muestreo", "Cada 3.0 seg"),
        ],
        icono=ft.Icons.THERMOSTAT,
        icono_color=AZUL,
    )

    # Ficha del Sensor LDR (Fotoresistencia)
    ficha_ldr = crear_ficha_hardware(
        titulo="SENSOR LDR (Luz)",
        estado_texto="OPERATIVO",
        estado_color=VERDE,
        pin_texto="GPIO 34 (ADC 12-bit)",
        especificaciones=[
            ("Resolución ADC", "0 - 4095 (11dB)"),
            ("Rango Escala", "0% a 100%"),
            ("Voltaje Op.", "3.3 V"),
            ("Lectura Raw", "819 (Actual)"),
        ],
        icono=ft.Icons.WB_SUNNY,
        icono_color=AMARILLO,
    )

    # Ficha del Actuador LED de Alerta
    ficha_led = crear_ficha_hardware(
        titulo="ACTUADOR LED ALERTA",
        estado_texto="AUTOMÁTICO / OK",
        estado_color=VERDE,
        pin_texto="GPIO 23 (Salida)",
        especificaciones=[
            ("Tipo", "Diodo LED indicador"),
            ("Lógica", "Activo en ALTO (3.3V)"),
            ("Disparador", "Temp > 39.0 °C"),
            ("Estado actual", "Apagado (Sin sobrecalentamiento)"),
        ],
        icono=ft.Icons.LIGHTBULB_OUTLINE,
        icono_color=VERDE,
    )

    # Ficha de la Pantalla OLED SSD1306
    ficha_oled = crear_ficha_hardware(
        titulo="PANTALLA OLED SSD1306",
        estado_texto="ACTIVA",
        estado_color=VERDE,
        pin_texto="I2C (SDA=21 | SCL=22)",
        especificaciones=[
            ("Resolución", "128 x 64 píxeles"),
            ("Controlador", "SSD1306 (Monocromático)"),
            ("Dirección I2C", "0x3C"),
            ("Refresco", "Cada 3.0 seg"),
        ],
        icono=ft.Icons.SMART_DISPLAY,
        icono_color=AZUL,
    )

    # Distribucion en 2 filas de 2 columnas que se reparten toda la altura
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(controls=[ficha_dht22, ficha_ldr], spacing=16, expand=True),
                ft.Row(controls=[ficha_led, ficha_oled], spacing=16, expand=True),
            ],
            spacing=16,
            expand=True,
        ),
        padding=20,
        expand=True,
    )
