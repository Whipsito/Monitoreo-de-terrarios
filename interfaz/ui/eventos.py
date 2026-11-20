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

# Panel contenedor que recibe la lista y la accion de exportacion
def crear_panel_eventos(lista_eventos, on_exportar=None):

    # Cabecera del panel centrada
    encabezado_panel = ft.Row(
        controls=[
            ft.Icon(ft.Icons.ARTICLE_OUTLINED, size=20, color=TEXTO_SEC),
            ft.Text("Registro de eventos", size=18, weight=ft.FontWeight.BOLD, color=TEXTO),
        ],
        spacing=8,
        alignment=ft.MainAxisAlignment.CENTER,
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
                on_click=on_exportar,
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


# Redibuja las filas visibles usando los eventos más recientes
def actualizar_lista_eventos(lista_eventos, eventos):
    filas = []
    for evento in eventos:
        es_alerta = evento["led"] == "ALTA"
        descripcion = (
            f"ALERTA: {evento['temperatura']} °C"
            if es_alerta
            else f"T:{evento['temperatura']} °C | H:{evento['humedad']}% | L:{evento['luz']}%"
        )
        filas.append(
            crear_evento(
                evento["hora"],
                descripcion,
                ROJO if es_alerta else VERDE,
                es_alerta=es_alerta,
            )
        )

    lista_eventos.controls = filas or [
        ft.Text("Esperando lecturas...", size=13, color=TEXTO_SEC)
    ]
