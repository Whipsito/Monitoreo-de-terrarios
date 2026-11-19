import flet as ft
from ui.estilos import *
from ui.graficas import crear_grafica_temperatura, crear_indicador_circular
from ui.eventos import crear_panel_eventos
from ui.sensores import crear_vista_sensores

# Tarjeta de metrica para mostrar valores de sensores
def crear_tarjeta(titulo, valor, unidad, icono, color, porcentaje=None, subtitulo_extra=None):

    # Cabecera de la tarjeta con titulo e icono representativo
    fila_superior = ft.Row(
        controls=[
            ft.Text(titulo, size=15, color=TEXTO_SEC),
            ft.Icon(icono, size=22, color=color),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # Valor principal con su unidad de medida
    fila_valor = ft.Row(
        controls=[
            ft.Text(valor, size=28, weight=ft.FontWeight.BOLD, color=TEXTO),
            ft.Text(unidad, size=14, color=color),
        ],
        spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.END,
    )

    # Barra de progreso o texto secundario segun el tipo de tarjeta
    if porcentaje is not None:
        elemento_inferior = ft.ProgressBar(
            value=porcentaje,
            color=color,
            bgcolor=PANEL_2,
            height=6,
            border_radius=4,
        )
    else:
        elemento_inferior = ft.Text(subtitulo_extra or "", size=13, color=TEXTO_SEC)

    # Contenedor final de la tarjeta
    return ft.Container(
        content=ft.Column(
            controls=[
                fila_superior,
                fila_valor,
                elemento_inferior,
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=PANEL,
        padding=16,
        border_radius=12,
        height=135,
        expand=True,
    )

# Configuracion y construccion de la ventana principal
def main(page: ft.Page):
    
    # Propiedades generales de la ventana unida a los bordes
    page.title = "TerraPapu"
    page.window.width = 1280
    page.window.height = 720
    page.window.resizable = True
    page.bgcolor = FONDO
    page.padding = 0

    # Estado de la barra lateral (inicia oculta)
    menu_abierto = False
    indice_seleccionado = 0
    opciones_menu = [
        ("Dashboard", ft.Icons.DASHBOARD),
        ("Sensores", ft.Icons.SENSORS),
        ("Configuración", ft.Icons.SETTINGS),
    ]

    # Alterna la visibilidad de la barra lateral
    def alternar_menu(e):
        nonlocal menu_abierto
        menu_abierto = not menu_abierto
        menu_lateral.visible = menu_abierto
        page.update()

    # Cambia la opcion seleccionada del menu manteniendo la barra abierta
    def seleccionar_opcion(indice):
        nonlocal indice_seleccionado
        indice_seleccionado = indice
        
        # Cambia la vista activa con la transicion animada
        area_contenido.content = vistas[indice]["contenido"]
        
        # Actualiza el titulo de la barra superior
        subtitulo_pantalla.value = vistas[indice]["titulo"]
        
        # Actualiza el boton seleccionado en el menu
        menu_lateral.content = construir_menu()
        
        page.update()

    # Construccion limpia de los botones del menu lateral
    def construir_menu():
        controles = []
        for indice, (nombre, icono) in enumerate(opciones_menu):
            color = AZUL if indice == indice_seleccionado else TEXTO_SEC
            controles.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(icono, color=color, size=20),
                            ft.Text(nombre, color=TEXTO, size=14),
                        ],
                        spacing=12,
                    ),
                    padding=10,
                    border_radius=8,
                    bgcolor=PANEL_2 if indice == indice_seleccionado else None,
                    on_click=lambda e, i=indice: seleccionar_opcion(i),
                )
            )
        return ft.Column(controles, spacing=8, expand=True)

    # Contenedor del menu lateral colapsable
    menu_lateral = ft.Container(
        content=construir_menu(),
        width=220,
        bgcolor=PANEL,
        padding=12,
        border_radius=0,
        visible=menu_abierto,
    )

    # Boton de menu en la barra superior
    boton_menu = ft.IconButton(
        icon=ft.Icons.MENU,
        icon_color=TEXTO,
        on_click=alternar_menu,
    )

    # Subtitulo que cambia dinamicamente segun la pantalla activa
    subtitulo_pantalla = ft.Text("Dashboard", size=16, color=TEXTO_SEC)

    # Titulo de la aplicacion con el boton de menu
    titulo = ft.Row(
        controls=[
            boton_menu,
            ft.Icon(ft.Icons.ECO, size=28, color=VERDE),
            ft.Text("TerraPapu", size=26, weight=ft.FontWeight.BOLD, color=TEXTO),
            subtitulo_pantalla,
        ],
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Indicador de estado de conexion con el dispositivo
    chip_conexion = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.CIRCLE, size=10, color=VERDE),
                ft.Text("Conectado", size=13, color=TEXTO),
            ],
            spacing=8,
        ),
        bgcolor=PANEL_2,
        padding=ft.Padding.symmetric(horizontal=12, vertical=6),
        border_radius=20,
    )

    # Etiqueta con la hora de la ultima lectura recibida
    texto_ultima_lectura = ft.Text(
        "Última: 20:34:10", 
        size=13, 
        color=TEXTO_SEC
    )

    # Grupo derecho que reune la conexion y la hora
    info_conexion = ft.Row(
        controls=[chip_conexion, texto_ultima_lectura],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Barra superior que ocupa todo el ancho de la ventana
    barra_superior = ft.Container(
        content=ft.Row(
            controls=[titulo, info_conexion],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=PANEL,
        padding=ft.Padding.symmetric(horizontal=16, vertical=10),
        height=70,
    )

    # Fila de tarjetas para las lecturas de los sensores
    tarjetas = ft.Row(
        controls=[
            crear_tarjeta(
                titulo="Temperatura", 
                valor="25.4", 
                unidad="°C", 
                icono=ft.Icons.THERMOSTAT, 
                color=AZUL, 
                porcentaje=0.50 
            ),
            crear_tarjeta(
                titulo="Humedad", 
                valor="62.0", 
                unidad="%", 
                icono=ft.Icons.WATER_DROP, 
                color=AZUL, 
                porcentaje=0.62 
            ),
            crear_tarjeta(
                titulo="Luminosidad", 
                valor="80", 
                unidad="%", 
                icono=ft.Icons.WB_SUNNY, 
                color=AMARILLO, 
                porcentaje=0.80 
            ),
            crear_tarjeta(
                titulo="Estado LED", 
                valor="OK", 
                unidad="", 
                icono=ft.Icons.LIGHTBULB_OUTLINE, 
                color=VERDE, 
                subtitulo_extra="LED: OFF"
            ),
        ],
        spacing=16,
    )

    # Fila de medidores circulares para humedad y luminosidad
    medidores_circulares = ft.Row(
        controls=[
            crear_indicador_circular(
                titulo="Humedad Relativa", 
                valor_texto="62%", 
                porcentaje=0.62, 
                icono=ft.Icons.WATER_DROP, 
                color=AZUL
            ),
            crear_indicador_circular(
                titulo="Luminosidad LDR", 
                valor_texto="80%", 
                porcentaje=0.80, 
                icono=ft.Icons.WB_SUNNY, 
                color=AMARILLO
            ),
        ],
        spacing=16,
    )

    # Panel que contiene la grafica de temperatura y los medidores circulares
    panel_grafica = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.SHOW_CHART, size=20, color=AZUL),
                        ft.Text("Historial de temperatura", size=18, weight=ft.FontWeight.BOLD, color=TEXTO),
                        ft.Text("(Últimas mediciones)", size=13, color=TEXTO_SEC),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                crear_grafica_temperatura(),
                medidores_circulares,
            ],
            spacing=16,
            expand=True,
        ),
        bgcolor=PANEL,
        padding=16,
        border_radius=12,
        expand=3,
    )

    # Panel que muestra la lista de eventos
    panel_eventos = crear_panel_eventos()

    # Seccion inferior que agrupa la grafica con medidores y los eventos
    seccion_inferior = ft.Row(
        [panel_grafica, panel_eventos],
        spacing=16,
        expand=2,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    # Vista 0: Dashboard con margen interno
    cuerpo_dashboard = ft.Container(
        content=ft.Column(
            controls=[tarjetas, seccion_inferior],
            spacing=20,
            expand=True,
        ),
        padding=20,
        expand=True,
    )

    # Vista 1: Sensores y Diagnostico de Hardware
    vista_sensores = crear_vista_sensores()

    # Mapeo de vistas para la navegacion
    vistas = [
        {"contenido": cuerpo_dashboard, "titulo": "Dashboard"},
        {"contenido": vista_sensores, "titulo": "Estado de Hardware"},
        {"contenido": cuerpo_dashboard, "titulo": "Configuración"},
    ]

    # Contenedor con transicion suave (FADE) entre vistas
    area_contenido = ft.AnimatedSwitcher(
        content=vistas[0]["contenido"],
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=300,
        reverse_duration=300,
        expand=True,
    )

    # Estructura principal con barra superior fija y contenido dinamico
    page.add(
        ft.Column(
            controls=[
                barra_superior,
                ft.Row(
                    controls=[menu_lateral, area_contenido],
                    spacing=0,
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
            ],
            spacing=0,
            expand=True,
        )
    )

# Punto de inicio de la aplicacion
ft.run(main)
