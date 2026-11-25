import flet as ft
from services.catalogo_sensores import VISUALIZACIONES
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
                ft.Column(controls=filas_specs, spacing=8),
            ],
            spacing=10,
        ),
        bgcolor=PANEL,
        padding=20,
        border_radius=12,
        col={"xs": 12, "md": 6},
    )

# Genera la vista completa de diagnostico de hardware ocupando toda la pantalla
def crear_ficha_sensor_agregado(sensor, on_editar, on_eliminar):
    return ft.Container(
        col={"xs": 12, "md": 6},
        bgcolor=PANEL,
        padding=20,
        border_radius=12,
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(sensor["nombre"], size=16, color=TEXTO, weight=ft.FontWeight.BOLD, expand=True),
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color=TEXTO, tooltip="Editar sensor", on_click=on_editar),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ROJO,
                            tooltip="Eliminar sensor",
                            on_click=on_eliminar,
                        ),
                    ],
                    spacing=0,
                ),
                ft.Text(sensor["descripcion"], size=13, color=TEXTO_SEC),
                ft.Text(f"Pines: {sensor['pines']}", size=13, color=TEXTO),
                ft.Text(VISUALIZACIONES[sensor["visualizacion"]], size=13, color=AZUL),
            ],
            spacing=6,
        ),
    )


def abrir_formulario_sensor(page, on_guardar, on_cerrar, sensor=None):
    editando = sensor is not None
    datos = sensor or {}
    nombre = ft.TextField(label="Nombre", value=datos.get("nombre", ""), max_length=40, autofocus=True)
    descripcion = ft.TextField(
        label="Descripción", value=datos.get("descripcion", ""), multiline=True, max_lines=4, max_length=240
    )
    pines = ft.TextField(
        label="Pines", value=datos.get("pines", ""), hint_text="Ejemplo: GPIO 32 o SDA 21, SCL 22", max_length=80
    )
    visualizacion = ft.Dropdown(
        label="Visualización en Dashboard",
        value=datos.get("visualizacion", "grafica"),
        options=[ft.dropdown.Option(key=clave, text=texto) for clave, texto in VISUALIZACIONES.items()],
    )
    error = ft.Text(color=ROJO, visible=False)

    async def cerrar(e):
        on_cerrar()

    async def cancelar(e):
        on_cerrar()
        page.pop_dialog()

    async def guardar(e):
        try:
            on_guardar(nombre.value, descripcion.value, pines.value, visualizacion.value)
        except (ValueError, OSError) as problema:
            error.value = str(problema) if isinstance(problema, ValueError) else "No se pudo guardar el sensor."
            error.visible = True
            page.update()
            return
        on_cerrar()
        page.pop_dialog()
        page.update()

    page.show_dialog(ft.AlertDialog(
        modal=True,
        title=ft.Text("Editar sensor" if editando else "Agregar sensor"),
        content=ft.Column(
            controls=[nombre, descripcion, pines, visualizacion, error],
            width=360,
            tight=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        actions=[
            ft.Button(content="Cancelar", on_click=cancelar),
            ft.Button(content="Guardar cambios" if editando else "Agregar", on_click=guardar),
        ],
        on_dismiss=cerrar,
    ))


def crear_vista_sensores(fichas_agregadas, on_agregar, aviso_sensores):
    
    # Ficha del Sensor DHT22
    ficha_dht22 = crear_ficha_hardware(
        titulo="SENSOR DHT22",
        estado_texto="FICHA TÉCNICA",
        estado_color=TEXTO_SEC,
        pin_texto="GPIO 4 (Digital)",
        especificaciones=[
            ("Rango Temp", "-40 °C a 80 °C"),
            ("Precisión T", "±0.5 °C"),
            ("Rango Hum", "0% a 100% HR"),
            ("Muestreo previsto", "Cada 3.0 seg en el firmware"),
        ],
        icono=ft.Icons.THERMOSTAT,
        icono_color=AZUL,
    )

    # Ficha del Sensor LDR (Fotoresistencia)
    ficha_ldr = crear_ficha_hardware(
        titulo="SENSOR LDR (Luz)",
        estado_texto="FICHA TÉCNICA",
        estado_color=TEXTO_SEC,
        pin_texto="GPIO 34 (ADC 12-bit)",
        especificaciones=[
            ("Resolución ADC", "0 - 4095 (11dB)"),
            ("Rango Escala", "0% a 100%"),
            ("Voltaje Op.", "3.3 V"),
            ("Lectura en Dashboard", "Luminosidad en porcentaje"),
        ],
        icono=ft.Icons.WB_SUNNY,
        icono_color=AMARILLO,
    )

    # Ficha del Actuador LED de Alerta
    ficha_led = crear_ficha_hardware(
        titulo="ACTUADOR LED ALERTA",
        estado_texto="FICHA TÉCNICA",
        estado_color=TEXTO_SEC,
        pin_texto="GPIO 23 (Salida)",
        especificaciones=[
            ("Tipo", "Diodo LED indicador"),
            ("Lógica", "Activo en ALTO (3.3V)"),
            ("Disparador del firmware", "Temp > 39.0 °C"),
            ("Estado", "Visible en el Dashboard"),
        ],
        icono=ft.Icons.LIGHTBULB_OUTLINE,
        icono_color=VERDE,
    )

    # Ficha de la Pantalla OLED SSD1306
    ficha_oled = crear_ficha_hardware(
        titulo="PANTALLA OLED SSD1306",
        estado_texto="FICHA TÉCNICA",
        estado_color=TEXTO_SEC,
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

    fichas_base = (ficha_dht22, ficha_ldr, ficha_led, ficha_oled)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Sensores y componentes", size=21, color=TEXTO, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            icon_color=TEXTO,
                            bgcolor=PANEL_2,
                            tooltip="Agregar sensor",
                            on_click=on_agregar,
                        ),
                    ],
                ),
                aviso_sensores,
                fichas_agregadas,
                ft.ResponsiveRow(controls=list(fichas_base), spacing=16, run_spacing=16),
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        expand=True,
    )
