import asyncio
from collections import deque
from http.client import HTTPException
from math import ceil, floor
from pathlib import Path
from time import monotonic

import flet as ft
import flet_charts as fch
import ui.estilos as estilos
from ui.estilos import *
from ui.graficas import crear_grafica_linea, crear_indicador_circular, crear_panel_sensor
from ui.eventos import crear_panel_eventos, actualizar_lista_eventos
from ui.formato import formatear_medicion
from ui.sensores import abrir_formulario_sensor, crear_ficha_sensor_agregado, crear_vista_sensores
from ui.configuracion import crear_vista_configuracion
from services.simulador import generar_lectura_simulada, generar_valor_sensor
from services.catalogo_sensores import agregar_sensor, cargar_sensores, editar_sensor, eliminar_sensor
from services.registro_eventos import RegistroEventos
from services.recibir_datos import recibir_lectura
from services.alertas import notificar_escritorio, reproducir_alerta
from services.preferencias import (
    PREDETERMINADAS,
    cargar_preferencias,
    guardar_preferencias,
    validar_preferencias,
)


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
    page.window.icon = str(Path(__file__).resolve().parent / "assets" / "app.ico")
    page.window.width = 1280
    page.window.height = 720
    page.window.resizable = True
    preferencias = cargar_preferencias()
    sensores_agregados = cargar_sensores()
    historial_sensores = {sensor["id"]: deque(maxlen=20) for sensor in sensores_agregados}
    aplicar_tema(preferencias["tema"])
    page.bgcolor = FONDO
    page.padding = 0
    modo_simulacion = {"activo": False}
    estado_datos = {
        "lectura": None,
        "hora": None,
    }
    estado_esp32 = "buscando"
    version_fuente = 0
    ultimo_id_esp32 = None
    senal_interrumpida = False
    alerta_activa = False
    proxima_lectura = monotonic()
    intervalo_csv = 3600
    proximo_csv = monotonic() + intervalo_csv
    cambios_sin_exportar = False
    confirmacion_abierta = False
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

    def informar(mensaje):
        if not confirmacion_abierta:
            page.show_dialog(ft.SnackBar(content=ft.Text(mensaje)))

    def emitir_alerta(mensaje, con_sonido):
        informar(mensaje)
        try:
            if con_sonido:
                reproducir_alerta()
            if preferencias["notificaciones"]:
                notificar_escritorio(mensaje)
        except (OSError, RuntimeError):
            informar("Windows no pudo emitir el aviso de escritorio o el sonido.")

    def exportar_eventos():
        nonlocal cambios_sin_exportar
        if not registro.eventos:
            informar("Todavía no hay eventos para exportar.")
            return
        try:
            ruta_csv = registro.exportar_csv()
        except OSError:
            informar("No se pudo guardar el CSV. Revisa el acceso a la carpeta exports.")
            return
        cambios_sin_exportar = False
        informar(f"CSV guardado en exports: {ruta_csv.name}")

    def confirmar(titulo, mensaje, accion):
        nonlocal confirmacion_abierta

        async def al_cerrar(e):
            nonlocal confirmacion_abierta
            confirmacion_abierta = False

        async def cancelar(e):
            await al_cerrar(e)
            page.pop_dialog()

        async def aceptar(e):
            await al_cerrar(e)
            page.pop_dialog()
            accion()

        confirmacion_abierta = True
        page.show_dialog(ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo),
            content=ft.Text(mensaje),
            on_dismiss=al_cerrar,
            actions=[
                ft.Button(content="Cancelar", on_click=cancelar),
                ft.Button(content="Confirmar", on_click=aceptar),
            ],
        ))

    def guardar_configuracion(datos):
        nonlocal alerta_activa, proxima_lectura, proximo_csv
        try:
            nuevas = validar_preferencias(datos)
            guardar_preferencias(nuevas)
        except ValueError as error:
            informar(str(error))
            return
        except OSError:
            informar("No se pudo guardar la configuración local.")
            return
        if preferencias["intervalo"] != nuevas["intervalo"]:
            proxima_lectura = monotonic() + nuevas["intervalo"]
        if preferencias["csv_automatico"] != nuevas["csv_automatico"]:
            proximo_csv = monotonic() + intervalo_csv
        if preferencias["umbral"] != nuevas["umbral"]:
            alerta_activa = False
        cambio_url = preferencias["url"] != nuevas["url"]
        preferencias.update(nuevas)
        if cambio_url and not modo_simulacion["activo"]:
            reiniciar_fuente()
        controles_simulacion["nombre"].value = preferencias["nombre"]
        page.update()
        informar("Configuración guardada.")

    async def restablecer(e):
        def aplicar_valores():
            nonlocal senal_interrumpida, proximo_csv
            try:
                guardar_preferencias(PREDETERMINADAS)
            except OSError:
                informar("No se pudieron guardar los valores predeterminados.")
                return
            preferencias.update(PREDETERMINADAS)
            modo_simulacion["activo"] = False
            senal_interrumpida = False
            reiniciar_fuente()
            proximo_csv = monotonic() + intervalo_csv
            aplicar_tema(preferencias["tema"])
            page.bgcolor = FONDO
            construir_interfaz()
            informar("Se restauraron los valores predeterminados.")

        confirmar("Restablecer configuración", "Se guardarán los valores predeterminados.", aplicar_valores)

    async def limpiar_historial(e):
        def limpiar():
            nonlocal cambios_sin_exportar
            registro.limpiar()
            for historial in historial_sensores.values():
                historial.clear()
            cambios_sin_exportar = False
            actualizar_historial()
            actualizar_sensores_agregados()
            page.update()
            informar("Historial de la sesión limpiado.")

        confirmar("Limpiar historial", "Se borrarán los eventos y los puntos de la gráfica de esta sesión.", limpiar)

    def cambiar_tema(nombre, borrador):
        if nombre == preferencias["tema"]:
            return
        preferencias["tema"] = nombre
        aplicar_tema(nombre)
        page.bgcolor = FONDO
        construir_interfaz(borrador)

    def construir_interfaz(borrador=None):
        tema_claro = estilos.TEMA_ACTUAL == "Claro"
        page.theme_mode = ft.ThemeMode.LIGHT if tema_claro else ft.ThemeMode.DARK
        color_texto_menu = "#172554" if tema_claro else TEXTO
        color_seleccion_menu = "#DBEAFE" if tema_claro else PANEL_2
        page.controls.clear()

        # Alterna la visibilidad de la barra lateral
        async def alternar_menu(e):
            nonlocal menu_abierto
            menu_abierto = not menu_abierto
            menu_lateral.visible = menu_abierto
            page.update()

        # Cambia la opcion seleccionada del menu manteniendo la barra abierta
        def seleccionar_opcion(indice):
            nonlocal indice_seleccionado
            if indice == indice_seleccionado:
                return
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
            def crear_accion(indice):
                async def navegar(e):
                    seleccionar_opcion(indice)
                return navegar

            controles = []
            for indice, (nombre, icono) in enumerate(opciones_menu):
                seleccionada = indice == indice_seleccionado
                color = ("#1D4ED8" if tema_claro else AZUL) if seleccionada else color_texto_menu
                controles.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(icono, color=color, size=20),
                                ft.Text(
                                    nombre,
                                    color=color_texto_menu,
                                    size=14,
                                    weight=ft.FontWeight.BOLD if seleccionada else ft.FontWeight.NORMAL,
                                ),
                            ],
                            spacing=12,
                        ),
                        padding=10,
                        border_radius=8,
                        bgcolor=color_seleccion_menu if seleccionada else None,
                        on_click=crear_accion(indice),
                    )
                )
            return ft.Column(controles, spacing=8, expand=True)

        # Contenedor del menu lateral colapsable
        menu_lateral = ft.Container(
            content=construir_menu(),
            width=220,
            bgcolor="#F8FAFC" if tema_claro else PANEL,
            padding=12,
            border_radius=0,
            visible=menu_abierto,
        )

        # Boton de menu en la barra superior
        boton_menu = ft.IconButton(
            icon=ft.Icons.MENU,
            icon_color=color_texto_menu,
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
                            "",
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
        texto_ultima_lectura = ft.Text(size=13, color=TEXTO_SEC)

        def cambiar_modo_simulacion(e):
            nonlocal senal_interrumpida
            modo_simulacion["activo"] = e.control.value
            senal_interrumpida = False
            reiniciar_fuente()
            page.update()

        async def cambiar_ecosistema(e):
            nonlocal proxima_lectura
            if e.control.value:
                preferencias["ecosistema"] = e.control.value
                estado_datos["lectura_anterior"] = None
                proxima_lectura = monotonic()

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
                    valor="—",
                    unidad="°C", 
                    icono=ft.Icons.THERMOSTAT, 
                    color=AZUL, 
                    porcentaje=0
                ),
                crear_tarjeta(
                    titulo="Humedad", 
                    valor="—",
                    unidad="%", 
                    icono=ft.Icons.WATER_DROP, 
                    color=AZUL, 
                    porcentaje=0
                ),
                crear_tarjeta(
                    titulo="Luminosidad", 
                    valor="—",
                    unidad="%", 
                    icono=ft.Icons.WB_SUNNY, 
                    color=AMARILLO, 
                    porcentaje=0
                ),
                crear_tarjeta(
                    titulo="Estado LED", 
                    valor="—",
                    unidad="", 
                    icono=ft.Icons.LIGHTBULB_OUTLINE, 
                    color=VERDE, 
                    subtitulo_extra="Sin lecturas"
                ),
            ],
            spacing=16,
        )

        # Fila de medidores circulares para humedad y luminosidad
        medidores_circulares = ft.Row(
            controls=[
                crear_indicador_circular(
                    titulo="Humedad Relativa", 
                    valor_texto="—",
                    porcentaje=0,
                    icono=ft.Icons.WATER_DROP, 
                    color=AZUL
                ),
                crear_indicador_circular(
                    titulo="Luminosidad LDR", 
                    valor_texto="—",
                    porcentaje=0,
                    icono=ft.Icons.WB_SUNNY, 
                    color=AMARILLO
                ),
            ],
            spacing=16,
        )

        grafica_temperatura = crear_grafica_linea()

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
                    (nombre_terrario := ft.Text(preferencias["nombre"], size=13, color=TEXTO_SEC)),
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

        # Panel que muestra las lecturas y permite exportarlas
        async def exportar_manualmente(e):
            exportar_eventos()

        panel_eventos = crear_panel_eventos(lista_eventos, exportar_manualmente)

        # Seccion inferior que agrupa la grafica con medidores y los eventos
        seccion_inferior = ft.Row(
            [panel_grafica, panel_eventos],
            spacing=16,
            expand=2,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        paneles_agregados = ft.ResponsiveRow(spacing=12, run_spacing=12)
        fichas_agregadas = ft.ResponsiveRow(spacing=16, run_spacing=16)
        actualizadores_sensores = {}
        seccion_agregados = ft.Column(
            [
                ft.Text("Sensores agregados", size=18, color=TEXTO, weight=ft.FontWeight.BOLD),
                ft.Text("Datos de prueba en modo simulación", size=13, color=TEXTO_SEC),
                paneles_agregados,
            ],
            spacing=8,
        )

        dashboard = ft.Column(
            controls=[seccion_agregados, tarjetas, seccion_inferior],
            spacing=20,
            expand=True,
        )

        def mostrar_sensor(sensor):
            tarjeta, actualizar = crear_panel_sensor(sensor)
            identificador = sensor["id"]

            async def editar(e):
                abrir_editor_sensor(sensor)

            async def eliminar(e):
                if confirmacion_abierta:
                    return

                def borrar():
                    try:
                        eliminar_sensor(sensores_agregados, identificador)
                    except (OSError, ValueError):
                        informar("No se pudo eliminar el sensor del catálogo.")
                        return
                    historial_sensores.pop(identificador, None)
                    reconstruir_sensores_agregados()
                    page.update()

                confirmar(
                    "Eliminar sensor",
                    f"Se borrará «{sensor['nombre']}» de Sensores y del Dashboard.",
                    borrar,
                )

            actualizar(historial_sensores[identificador])
            actualizadores_sensores[identificador] = actualizar
            paneles_agregados.controls.append(tarjeta)
            fichas_agregadas.controls.append(crear_ficha_sensor_agregado(sensor, editar, eliminar))

        def ajustar_dashboard():
            hay_sensores = bool(sensores_agregados)
            seccion_agregados.visible = hay_sensores
            fichas_agregadas.visible = hay_sensores
            dashboard.scroll = ft.ScrollMode.AUTO if hay_sensores else None
            seccion_inferior.expand = None if hay_sensores else 2
            seccion_inferior.height = 450 if hay_sensores else None

        def reconstruir_sensores_agregados():
            paneles_agregados.controls.clear()
            fichas_agregadas.controls.clear()
            actualizadores_sensores.clear()
            for sensor in sensores_agregados:
                mostrar_sensor(sensor)
            ajustar_dashboard()

        def abrir_editor_sensor(sensor=None):
            nonlocal confirmacion_abierta
            if confirmacion_abierta:
                return

            def guardar(nombre, descripcion, pines, visualizacion):
                if sensor is None:
                    nuevo = agregar_sensor(sensores_agregados, nombre, descripcion, pines, visualizacion)
                    historial_sensores[nuevo["id"]] = deque(maxlen=20)
                else:
                    editar_sensor(sensores_agregados, sensor["id"], nombre, descripcion, pines, visualizacion)
                reconstruir_sensores_agregados()

            def cerrar_formulario():
                nonlocal confirmacion_abierta
                confirmacion_abierta = False

            confirmacion_abierta = True
            abrir_formulario_sensor(page, guardar, cerrar_formulario, sensor)

        async def abrir_alta_sensor(e):
            abrir_editor_sensor()

        reconstruir_sensores_agregados()

        # Vista 0: Dashboard con margen interno
        cuerpo_dashboard = ft.Container(
            content=dashboard,
            padding=20,
            expand=True,
        )

        # Vista 1: Sensores y Diagnostico de Hardware
        aviso_sensores = ft.Text(
            "El ESP32 está conectado. Aún no hay mediciones de los sensores.",
            size=14,
            color=TEXTO,
            visible=False,
        )
        vista_sensores = crear_vista_sensores(fichas_agregadas, abrir_alta_sensor, aviso_sensores)

        # Vista 2: Configuracion del Sistema (con callback de cambio de tema)
        vista_configuracion = crear_vista_configuracion(
            preferencias=borrador if borrador is not None else preferencias,
            simulacion_activa=modo_simulacion["activo"],
            senal_interrumpida=senal_interrumpida,
            on_cambiar_tema=cambiar_tema,
            on_cambiar_simulacion=cambiar_modo_simulacion,
            on_cambiar_ecosistema=cambiar_ecosistema,
            on_guardar=guardar_configuracion,
            on_restablecer=restablecer,
            on_limpiar=limpiar_historial,
            on_prueba_termica=probar_alerta_termica,
            on_alternar_senal=alternar_senal,
        )

        # Mapeo de vistas para la navegacion
        vistas = [
            {"contenido": cuerpo_dashboard, "titulo": "Dashboard"},
            {"contenido": vista_sensores, "titulo": "Estado de Hardware"},
            {"contenido": vista_configuracion, "titulo": "Configuración"},
        ]
        for indice, vista in enumerate(vistas):
            vista["contenido"].key = f"vista-{indice}"

        controles_simulacion.update(
            tarjetas=tarjetas.controls,
            medidores=medidores_circulares.controls,
            grafica=grafica_temperatura,
            hora=texto_ultima_lectura,
            estado=texto_estado_conexion,
            punto=chip_conexion.content.controls[0],
            nombre=nombre_terrario,
            lista_eventos=lista_eventos,
            sensores=actualizadores_sensores,
            aviso_sensores=aviso_sensores,
        )

        # Solo se desvanece el contenido al navegar.
        area_contenido = ft.AnimatedSwitcher(
            content=vistas[indice_seleccionado]["contenido"],
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=160,
            reverse_duration=120,
            expand=True,
        )
        actualizar_estado_conexion()
        actualizar_mediciones()
        actualizar_historial()

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

    def actualizar_estado_conexion():
        if senal_interrumpida:
            estado, color = "Señal simulada interrumpida", ROJO
        elif modo_simulacion["activo"]:
            estado, color = "Modo simulación", VERDE
        else:
            estado, color = {
                "buscando": ("Buscando ESP32", TEXTO_SEC),
                "conectado": ("ESP32 conectado", VERDE),
                "sin_datos": ("ESP32 conectado · Sin mediciones", VERDE),
                "sin_conexion": ("ESP32 sin conexión", ROJO),
                "respuesta_invalida": ("Respuesta del ESP32 inválida", ROJO),
            }[estado_esp32]
        controles_simulacion["estado"].value = estado
        controles_simulacion["punto"].color = color
        controles_simulacion["aviso_sensores"].visible = (
            not modo_simulacion["activo"] and estado_esp32 == "sin_datos"
        )
        hora = estado_datos["hora"]
        origen = "simulada" if modo_simulacion["activo"] else "del ESP32"
        controles_simulacion["hora"].value = (
            f"Última {origen}: {hora}" if hora else "Sin lecturas"
        )

    def reiniciar_fuente():
        nonlocal version_fuente, estado_esp32, ultimo_id_esp32, proxima_lectura, alerta_activa
        version_fuente += 1
        estado_esp32 = "buscando"
        ultimo_id_esp32 = None
        proxima_lectura = monotonic()
        alerta_activa = False
        estado_datos.update(lectura=None, hora=None, lectura_anterior=None)
        for historial in historial_sensores.values():
            historial.clear()
        actualizar_sensores_agregados()
        actualizar_mediciones()
        actualizar_historial()
        actualizar_estado_conexion()

    def actualizar_sensores_agregados():
        for identificador, actualizar in controles_simulacion["sensores"].items():
            actualizar(historial_sensores[identificador])

    def actualizar_mediciones():
        lectura = estado_datos["lectura"]
        tarjetas = controles_simulacion["tarjetas"]
        if lectura is None:
            lecturas = ("—", "—", "—")
            barras = (0, 0, 0)
        else:
            temperatura, humedad, luz = (lectura[clave] for clave in ("temperatura", "humedad", "luz"))
            lecturas = (temperatura, humedad, luz)
            barras = (max(0, min(1, temperatura / 50)), humedad / 100, luz / 100)
        for tarjeta, valor, barra in zip(tarjetas, lecturas, barras):
            tarjeta.content.controls[1].controls[0].value = formatear_medicion(valor) if lectura else "—"
            tarjeta.content.controls[2].value = barra

        for medidor, valor, barra in zip(controles_simulacion["medidores"], lecturas[1:], barras[1:]):
            anillo = medidor.content.controls[1]
            anillo.controls[0].value = barra
            anillo.controls[1].content.value = f"{formatear_medicion(valor)}%" if lectura else "—"

        led_encendido = lectura is not None and lectura["led"] == "ALTA"
        tarjeta_led = tarjetas[3].content
        tarjeta_led.controls[0].controls[1].color = ROJO if led_encendido else VERDE
        tarjeta_led.controls[1].controls[0].value = lectura["led"] if lectura else "—"
        tarjeta_led.controls[2].value = ("LED: ON" if led_encendido else "LED: OFF") if lectura else "Sin lecturas"

    def actualizar_historial():
        eventos = registro.obtener_recientes()
        actualizar_lista_eventos(controles_simulacion["lista_eventos"], eventos)
        grafica = controles_simulacion["grafica"]
        temperaturas = [
            evento["temperatura"]
            for evento in registro.eventos
            if (evento["origen"] != "esp32") == modo_simulacion["activo"]
        ][:20][::-1]
        grafica.data_series[0].points = [
            fch.LineChartDataPoint(indice, round(valor, 1)) for indice, valor in enumerate(temperaturas)
        ]
        grafica.max_x = max(5, len(temperaturas) - 1)
        grafica.min_y = 5 * floor(min([20, *temperaturas]) / 5)
        grafica.max_y = 5 * ceil(max([40, *temperaturas]) / 5)
        paso = 5 if grafica.max_y - grafica.min_y <= 30 else 10
        grafica.horizontal_grid_lines.interval = paso
        grafica.left_axis.labels = [
            fch.ChartAxisLabel(value=valor, label=ft.Text(f"{valor} °C", size=11, color=TEXTO_SEC))
            for valor in range(grafica.min_y, grafica.max_y + 1, paso)
        ]

    def registrar_lectura(lectura, prueba=False, origen="simulacion"):
        nonlocal alerta_activa, cambios_sin_exportar
        evento = registro.agregar_lectura(lectura, prueba=prueba, origen=origen)
        cambios_sin_exportar = True
        estado_datos["lectura"] = lectura
        estado_datos["hora"] = evento["hora"]
        actualizar_mediciones()
        actualizar_historial()
        actualizar_estado_conexion()
        page.update()

        hay_alerta = lectura["led"] == "ALTA"
        aviso = hay_alerta and (prueba or not alerta_activa)
        if not prueba:
            alerta_activa = hay_alerta
        if aviso:
            temperatura = formatear_medicion(lectura["temperatura"])
            mensaje = f"Temperatura alta: {temperatura} °C"
            if prueba:
                mensaje = f"Prueba de alerta: {temperatura} °C"
            emitir_alerta(mensaje, preferencias["sonido_termico"])

    async def probar_alerta_termica(e):
        if not modo_simulacion["activo"]:
            return
        if senal_interrumpida:
            informar("Recupera la señal simulada para probar la alerta térmica.")
            return
        lectura = generar_lectura_simulada(preferencias["ecosistema"])
        lectura["temperatura"] = round(preferencias["umbral"] + 1, 1)
        lectura["led"] = "ALTA"
        registrar_lectura(lectura, prueba=True)

    async def alternar_senal(e):
        nonlocal senal_interrumpida, proxima_lectura, alerta_activa
        if not modo_simulacion["activo"]:
            return
        senal_interrumpida = not senal_interrumpida
        alerta_activa = False
        proxima_lectura = monotonic()
        e.control.content = "Recuperar señal" if senal_interrumpida else "Simular pérdida de señal"
        actualizar_estado_conexion()
        page.update()
        if senal_interrumpida:
            emitir_alerta("Se interrumpió la señal simulada.", preferencias["sonido_desconexion"])

    async def consultar_esp32():
        nonlocal estado_esp32, ultimo_id_esp32
        version = version_fuente
        lectura = None
        try:
            lectura = await asyncio.to_thread(recibir_lectura, preferencias["url"])
            estado = "conectado" if lectura else "sin_datos"
        except OSError:
            estado = "sin_conexion"
        except (ValueError, HTTPException):
            estado = "respuesta_invalida"

        if version != version_fuente:
            return  # Cambió el modo o la URL mientras se esperaba la respuesta.
        anterior = estado_esp32
        estado_esp32 = estado
        if lectura and lectura["id_lectura"] != ultimo_id_esp32:
            ultimo_id_esp32 = lectura["id_lectura"]
            registrar_lectura(lectura, origen="esp32")
        elif estado != anterior:
            actualizar_estado_conexion()
            page.update()
        if anterior in ("conectado", "sin_datos") and estado == "sin_conexion":
            emitir_alerta("Se perdió la conexión con el ESP32.", preferencias["sonido_desconexion"])

    async def actualizar_datos():
        nonlocal proxima_lectura, proximo_csv
        while True:
            ahora = monotonic()
            if not modo_simulacion["activo"] and ahora >= proxima_lectura:
                proxima_lectura = ahora + preferencias["intervalo"]
                await consultar_esp32()
                ahora = monotonic()
            elif modo_simulacion["activo"] and not senal_interrumpida and ahora >= proxima_lectura:
                proxima_lectura = ahora + preferencias["intervalo"]
                lectura = generar_lectura_simulada(
                    preferencias["ecosistema"],
                    estado_datos.get("lectura_anterior"),
                    preferencias["umbral"],
                )
                estado_datos["lectura_anterior"] = lectura
                for historial in historial_sensores.values():
                    anterior = historial[-1] if historial else None
                    historial.append(generar_valor_sensor(anterior))
                actualizar_sensores_agregados()
                registrar_lectura(lectura)
            if preferencias["csv_automatico"] and ahora >= proximo_csv:
                proximo_csv = ahora + intervalo_csv
                if cambios_sin_exportar:
                    exportar_eventos()
            await asyncio.sleep(0.25)

    construir_interfaz()
    page.run_task(actualizar_datos)

# Punto de inicio de la aplicacion
ft.run(main)
