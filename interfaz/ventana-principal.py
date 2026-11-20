import asyncio
from datetime import datetime

import flet as ft
import flet_charts as fch
from ui.estilos import *
from ui.graficas import crear_grafica_temperatura, crear_indicador_circular
from ui.eventos import crear_panel_eventos, actualizar_lista_eventos
from ui.sensores import crear_vista_sensores
from ui.configuracion import crear_vista_configuracion
from services.simulador import generar_lectura_simulada
from services.registro_eventos import RegistroEventos


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
    modo_simulacion = {"activo": False}
    estado_datos = {
        "ecosistema": "Tropical / Selva (Hum: 70-90% | Temp: 24-28°C)",
        "lectura": None,
    }
    registro = RegistroEventos()
    controles_simulacion = {}

    # Estado de la barra lateral y vista activa (persisten al cambiar de tema)
    menu_abierto = False
    indice_seleccionado = 0
    opciones_menu = [
        ("Dashboard", ft.Icons.DASHBOARD),
        ("Sensores", ft.Icons.SENSORS),
        ("Configuración", ft.Icons.SETTINGS),
    ]

    # Actualiza el fondo de la pagina y redibuja toda la interfaz con el nuevo tema
    def cambiar_tema():
        page.bgcolor = FONDO
        construir_interfaz()

    # Construye o reconstruye la interfaz completa manteniendo la pantalla activa
    def construir_interfaz():
        page.controls.clear()

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

        # Subtitulo que refleja la pantalla activa actual
        titulos_vistas = ["Dashboard", "Estado de Hardware", "Configuración"]
        subtitulo_pantalla = ft.Text(titulos_vistas[indice_seleccionado], size=16, color=TEXTO_SEC)

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
                    (
                        texto_estado_conexion := ft.Text(
                            "Modo simulación" if modo_simulacion["activo"] else "Esperando ESP32",
                            size=13,
                            color=TEXTO,
                        )
                    ),
                ],
                spacing=8,
            ),
            bgcolor=PANEL_2,
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            border_radius=20,
        )

        # Etiqueta con la hora de la ultima lectura recibida
        texto_ultima_lectura = ft.Text(
            "Datos de prueba" if modo_simulacion["activo"] else "Sin lecturas recibidas",
            size=13, 
            color=TEXTO_SEC
        )

        # Refleja en la barra superior el modo elegido en Configuración
        def cambiar_modo_simulacion(e):
            modo_simulacion["activo"] = e.control.value
            if e.control.value:
                texto_estado_conexion.value = "Modo simulación"
                texto_ultima_lectura.value = "Datos de prueba"
            else:
                texto_estado_conexion.value = "Esperando ESP32"
                texto_ultima_lectura.value = "Sin lecturas recibidas"
            page.update()

        # Guarda el ecosistema seleccionado para el siguiente ciclo de simulacion
        def cambiar_ecosistema(e):
            estado_datos["ecosistema"] = e.control.value
            estado_datos["lectura"] = None

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

        grafica_temperatura = crear_grafica_temperatura()

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
                    grafica_temperatura,
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

        # Lista que el simulador actualiza con cada lectura nueva
        lista_eventos = ft.Column(
            controls=[ft.Text("Esperando lecturas...", size=13, color=TEXTO_SEC)],
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        # Exporta el historial y muestra el nombre del archivo generado
        def exportar_eventos(e):
            ruta_csv = registro.exportar_csv()
            texto_ultima_lectura.value = f"CSV guardado: {ruta_csv.name}"
            page.update()

        # Panel que muestra las lecturas y permite exportarlas
        panel_eventos = crear_panel_eventos(lista_eventos, exportar_eventos)

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

        # Vista 2: Configuracion del Sistema (con callback de cambio de tema)
        vista_configuracion = crear_vista_configuracion(
            on_cambiar_tema=cambiar_tema,
            on_cambiar_simulacion=cambiar_modo_simulacion,
            on_cambiar_ecosistema=cambiar_ecosistema,
            simulacion_activa=modo_simulacion["activo"],
            ecosistema_seleccionado=estado_datos["ecosistema"],
        )

        # Mapeo de vistas para la navegacion
        vistas = [
            {"contenido": cuerpo_dashboard, "titulo": "Dashboard"},
            {"contenido": vista_sensores, "titulo": "Estado de Hardware"},
            {"contenido": vista_configuracion, "titulo": "Configuración"},
        ]

        controles_simulacion.update(
            tarjetas=tarjetas.controls,
            medidores=medidores_circulares.controls,
            grafica=grafica_temperatura,
            hora=texto_ultima_lectura,
            lista_eventos=lista_eventos,
        )

        # Contenedor de la vista activa sin transicion animada
        area_contenido = ft.Container(
            content=vistas[indice_seleccionado]["contenido"],
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
        page.update()

    # Carga inicial de la interfaz
    construir_interfaz()

    # Actualiza las tarjetas y la grafica cada tres segundos en modo demo
    async def actualizar_datos_simulados():
        while True:
            await asyncio.sleep(3)
            if not modo_simulacion["activo"] or not controles_simulacion:
                continue

            lectura = generar_lectura_simulada(
                estado_datos["ecosistema"],
                estado_datos["lectura"],
            )
            estado_datos["lectura"] = lectura
            registro.agregar_lectura(lectura)
            temperatura = lectura["temperatura"]
            humedad = lectura["humedad"]
            luz = lectura["luz"]
            led_encendido = lectura["led"] == "ALTA"

            lecturas = [temperatura, humedad, luz]
            barras = [temperatura / 50, humedad / 100, luz / 100]
            tarjetas_actuales = controles_simulacion["tarjetas"]

            for indice, valor in enumerate(lecturas):
                contenido = tarjetas_actuales[indice].content
                contenido.controls[1].controls[0].value = str(valor)
                contenido.controls[2].value = barras[indice]

            valores_medidores = [humedad, luz]
            porcentajes_medidores = [humedad / 100, luz / 100]
            for indice, valor in enumerate(valores_medidores):
                medidor = controles_simulacion["medidores"][indice].content
                anillo = medidor.controls[1]
                anillo.controls[0].value = porcentajes_medidores[indice]
                anillo.controls[1].content.value = f"{valor:.0f}%"

            tarjeta_led = tarjetas_actuales[3].content
            tarjeta_led.controls[1].controls[0].value = "ALTA" if led_encendido else "OK"
            tarjeta_led.controls[2].value = "LED: ON" if led_encendido else "LED: OFF"

            actualizar_lista_eventos(
                controles_simulacion["lista_eventos"],
                registro.obtener_recientes(),
            )

            grafica = controles_simulacion["grafica"]
            puntos_actuales = grafica.data_series[0].points
            valores_grafica = [punto.y for punto in puntos_actuales]
            valores_grafica = (valores_grafica + [temperatura])[-20:]
            grafica.data_series = [
                fch.LineChartData(
                    points=[
                        fch.LineChartDataPoint(indice, valor)
                        for indice, valor in enumerate(valores_grafica)
                    ],
                    color=AZUL,
                    stroke_width=3,
                    curved=True,
                    point=True,
                )
            ]
            grafica.max_x = max(5, len(valores_grafica) - 1)
            controles_simulacion["hora"].value = (
                f"Última: {datetime.now().strftime('%H:%M:%S')}"
            )
            page.update()

    page.run_task(actualizar_datos_simulados)

# Punto de inicio de la aplicacion
ft.run(main)
