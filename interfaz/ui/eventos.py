import flet as ft
from ui.estilos import *

# Fila individual para un registro o evento con estilo de tarjeta
def crear_evento(hora, descripcion, color, es_alerta=False):
    # Icono segun si es una lectura normal o una alerta critica
    icono_estado = ft.Icon(
        ft.Icons.WARNING_AMBER_ROUNDED if es_alerta else ft.Icons.CIRCLE,
        size=14 if es_alerta else 8,
        color=color,
    )

    # Contenido horizontal: hora a la izquierda y mediciones a la derecha
    fila_contenido = ft.Row(
        controls=[
            ft.Row(
                controls=[
                    icono_estado,
                    ft.Text(hora, size=13, color=TEXTO_SEC),
                ],
                spacing=8,
            ),
            ft.Text(
                descripcion, 
                size=13, 
                color=ROJO if es_alerta else TEXTO, 
                weight=ft.FontWeight.BOLD if es_alerta else ft.FontWeight.NORMAL
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Contenedor que le da cuerpo y fondo a cada evento
    return ft.Container(
        content=fila_contenido,
        bgcolor=PANEL_2,
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        border_radius=8,
    )

# Panel contenedor de la lista de eventos y boton de exportacion
def crear_panel_eventos():

    # Cabecera del panel centrada
    encabezado_panel = ft.Row(
        controls=[
            ft.Icon(ft.Icons.ARTICLE_OUTLINED, size=20, color=TEXTO_SEC),
            ft.Text("Registro de eventos", size=18, weight=ft.FontWeight.BOLD, color=TEXTO),
        ],
        spacing=8,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Lista con las lecturas recientes con scroll automatico
    lista_eventos = ft.Column(
        controls=[
            crear_evento("20:34:10", "T:25.4 °C | H:62% | L:80%", VERDE),
            crear_evento("20:34:07", "T:25.3 °C | H:62% | L:80%", VERDE),
            crear_evento("20:34:04", "T:25.3 °C | H:61% | L:79%", VERDE),
            crear_evento("20:34:01", "ALERTA: Temp alta 39.5 °C", ROJO, es_alerta=True),
            crear_evento("20:33:58", "T:25.2 °C | H:60% | L:78%", VERDE),
        ],
        spacing=10,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    # Boton centrado para exportar a CSV
    boton_exportar = ft.Row(
        controls=[
            ft.Button(
                content="Exportar a CSV",
                icon=ft.Icons.FILE_DOWNLOAD,
                color=TEXTO,
                bgcolor=PANEL_2,
                height=38,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Contenedor final del panel
    return ft.Container(
        content=ft.Column(
            controls=[
                encabezado_panel,
                lista_eventos,
                boton_exportar,
            ],
            spacing=14,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=PANEL,
        padding=16,
        border_radius=12,
        expand=2,
    )