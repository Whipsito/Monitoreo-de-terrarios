import flet as ft
import ui.estilos as estilos
from ui.estilos import *


# Envuelve un TextField o Dropdown con su etiqueta por fuera y ancho completo
def crear_campo_etiquetado(etiqueta, control, expand=False):
    return ft.Column(
        controls=[
            ft.Text(etiqueta, size=12, color=TEXTO_SEC, weight=ft.FontWeight.W_500),
            control,
        ],
        spacing=4,
        expand=expand,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

# Tarjeta contenedora para agrupar secciones de configuracion
def crear_bloque_config(titulo, icono, icono_color, controles, alto=None):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(icono, size=20, color=icono_color),
                        ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD, color=TEXTO),
                    ],
                    spacing=8,
                ),
                ft.Divider(color=PANEL_2, height=1),
                ft.Column(controls=controles, spacing=12),
            ],
            spacing=12,
        ),
        bgcolor=PANEL,
        padding=18,
        border_radius=12,
        height=alto,
        expand=True,
    )

# Genera la vista completa de configuraciones del sistema
def crear_vista_configuracion(
    on_cambiar_tema=None,
    on_cambiar_simulacion=None,
    on_cambiar_ecosistema=None,
    simulacion_activa=False,
    ecosistema_seleccionado="Tropical / Selva (Hum: 70-90% | Temp: 24-28°C)",
):

    # 1. Seccion de perfil del terrario y tipo de especie
    campo_nombre = ft.TextField(
        value="Terrario Papu #1",
        bgcolor=PANEL_2,
        border_color=PANEL_2,
        color=TEXTO,
        height=42,
        text_size=13,
    )

    selector_ecosistema = ft.Dropdown(
        value=ecosistema_seleccionado,
        options=[
            ft.dropdown.Option(
                key="Tropical / Selva (Hum: 70-90% | Temp: 24-28°C)",
                text="Tropical / Selva (Hum: 70-90% | Temp: 24-28°C)",
                leading_icon=ft.Icons.FOREST,
            ),
            ft.dropdown.Option(
                key="Desértico / Árido (Hum: 15-30% | Temp: 28-36°C)",
                text="Desértico / Árido (Hum: 15-30% | Temp: 28-36°C)",
                leading_icon=ft.Icons.WB_SUNNY,
            ),
            ft.dropdown.Option(
                key="Templado / Bosque (Hum: 50-70% | Temp: 20-25°C)",
                text="Templado / Bosque (Hum: 50-70% | Temp: 20-25°C)",
                leading_icon=ft.Icons.PARK,
            ),
            ft.dropdown.Option(
                key="Personalizado",
                text="Personalizado",
                leading_icon=ft.Icons.TUNE,
            ),
        ],
        bgcolor=PANEL_2,
        border_color=PANEL_2,
        color=TEXTO,
        text_size=13,
        on_select=on_cambiar_ecosistema,
    )

    bloque_perfil = crear_bloque_config(
        titulo="Perfil del Terrario",
        icono=ft.Icons.PETS,
        icono_color=VERDE,
        controles=[
            crear_campo_etiquetado("Nombre del Terrario", campo_nombre),
            crear_campo_etiquetado("Ecosistema / Especie", selector_ecosistema),
        ],
        alto=235,
    )

    # 2. Seccion de apariencia y temas visuales (mismo alto que bloque_perfil)
    temas_info = {
        "Oscuro":         "#38BDF8",
        "Claro":          "#0284C7",
        "Verde Terrario": "#22C55E",
        "Nocturno Ámbar": "#F59E0B",
    }

    def seleccionar_tema(nombre_tema):
        aplicar_tema(nombre_tema)
        if on_cambiar_tema:
            on_cambiar_tema()

    opciones_tema = []
    for nombre_tema, color_acento in temas_info.items():
        es_activo = nombre_tema == estilos.TEMA_ACTUAL
        opciones_tema.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CIRCLE, size=12, color=color_acento),
                        ft.Text(nombre_tema, size=13, color=TEXTO, weight=ft.FontWeight.W_500),
                    ],
                    spacing=8,
                ),
                padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                bgcolor=PANEL_2 if es_activo else None,
                border_radius=8,
                border=ft.Border.all(1, AZUL if es_activo else PANEL_2),
                expand=True,
                ink=True,
                on_click=lambda e, t=nombre_tema: seleccionar_tema(t),
            )
        )

    fila_temas = ft.Row(controls=opciones_tema, spacing=8)

    bloque_temas = crear_bloque_config(
        titulo="Apariencia y Temas",
        icono=ft.Icons.PALETTE_OUTLINED,
        icono_color=MORADO,
        controles=[
            ft.Text("Selecciona la paleta de colores para el monitor:", size=13, color=TEXTO_SEC),
            fila_temas,
        ],
        alto=235,
    )

    # 3. Seccion de alertas y sonidos
    switch_notificaciones = ft.Row(
        controls=[
            ft.Text("Notificaciones de escritorio (Windows)", size=13, color=TEXTO),
            ft.Switch(
                value=True,
                active_color=VERDE,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    switch_beep = ft.Row(
        controls=[
            ft.Text("Alerta sonora (Beep) al superar 39.0 °C", size=13, color=TEXTO),
            ft.Switch(value=False, active_color=ROJO),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    switch_desconexion = ft.Row(
        controls=[
            ft.Text("Alerta sonora al perder señal de ESP32", size=13, color=TEXTO),
            ft.Switch(value=False, active_color=AMARILLO),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    bloque_alertas = crear_bloque_config(
        titulo="Alertas y Notificaciones",
        icono=ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED,
        icono_color=AMARILLO,
        controles=[switch_notificaciones, switch_beep, switch_desconexion],
        alto=225,
    )

    # 4. Seccion de simulacion y registro de datos
    switch_demo = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Modo Simulación / Demo", size=13, weight=ft.FontWeight.BOLD, color=TEXTO),
                    ft.Text("Genera datos de prueba sin necesidad de ESP32 físico", size=11, color=TEXTO_SEC),
                ],
                spacing=2,
            ),
            ft.Switch(
                value=simulacion_activa,
                active_color=VERDE,
                on_change=on_cambiar_simulacion,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    switch_csv_auto = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Guardado automático en CSV", size=13, color=TEXTO),
                    ft.Text("Guarda una copia del historial cada hora", size=11, color=TEXTO_SEC),
                ],
                spacing=2,
            ),
            ft.Switch(value=False, active_color=AZUL),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    boton_limpiar = ft.Button(
        content="Limpiar historial de eventos",
        icon=ft.Icons.DELETE_OUTLINE,
        color=ROJO,
        bgcolor=PANEL_2,
        height=36,
    )

    bloque_simulacion = crear_bloque_config(
        titulo="Simulación y Datos",
        icono=ft.Icons.SCIENCE_OUTLINED,
        icono_color=AZUL,
        controles=[switch_demo, switch_csv_auto, boton_limpiar],
        alto=225,
    )

    # 5. Seccion de umbrales y conexion de red
    campo_umbral = ft.TextField(
        value="39.0",
        bgcolor=PANEL_2,
        border_color=PANEL_2,
        color=TEXTO,
        height=42,
        text_size=13,
    )

    campo_intervalo = ft.TextField(
        value="3",
        bgcolor=PANEL_2,
        border_color=PANEL_2,
        color=TEXTO,
        height=42,
        text_size=13,
    )

    fila_umbrales = ft.Row(
        controls=[
            crear_campo_etiquetado("Umbral Alerta Térmica (°C)", campo_umbral, expand=True),
            crear_campo_etiquetado("Intervalo de Refresco (seg)", campo_intervalo, expand=True),
        ],
        spacing=12,
    )

    campo_url = ft.TextField(
        value="http://0.0.0.0:8000/datos",
        bgcolor=PANEL_2,
        border_color=PANEL_2,
        color=TEXTO,
        height=42,
        text_size=13,
    )

    bloque_red = crear_bloque_config(
        titulo="Umbrales y Red",
        icono=ft.Icons.LAN_OUTLINED,
        icono_color=AZUL,
        controles=[
            fila_umbrales,
            crear_campo_etiquetado("URL / Endpoint del Servidor", campo_url),
        ],
    )

    # 6. Botones de accion principales
    boton_guardar = ft.Button(
        content="Guardar Configuración",
        icon=ft.Icons.SAVE_OUTLINED,
        color=FONDO,
        bgcolor=VERDE,
        height=42,
    )

    boton_restablecer = ft.Button(
        content="Restablecer Valores",
        icon=ft.Icons.RESTORE,
        color=TEXTO,
        bgcolor=PANEL_2,
        height=42,
    )

    fila_botones = ft.Row(
        controls=[boton_restablecer, boton_guardar],
        alignment=ft.MainAxisAlignment.END,
        spacing=12,
    )

    # Retorna el contenedor con scroll que agrupa todas las secciones
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(controls=[bloque_perfil, bloque_temas], spacing=16),
                ft.Row(controls=[bloque_alertas, bloque_simulacion], spacing=16),
                bloque_red,
                fila_botones,
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=20,
        expand=True,
    )
