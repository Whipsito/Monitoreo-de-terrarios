import flet as ft
import flet_charts as fch
from ui.estilos import AZUL, AMARILLO, PANEL, PANEL_2, TEXTO, TEXTO_SEC

# Genera la grafica de linea para la temperatura
def crear_grafica_linea(valores=(), minimo=20, maximo=40, paso=5, unidad="°C"):

    # Serie de datos con los puntos de temperatura y puntos visibles
    serie_temperatura = fch.LineChartData(
        points=[
            fch.LineChartDataPoint(indice, valor)
            for indice, valor in enumerate(valores)
        ],
        color=AZUL,
        stroke_width=3,
        curved=True,
        point=True,
    )

    # Configuracion de ejes con valores de temperatura
    eje_izquierdo = fch.ChartAxis(
        labels=[
            fch.ChartAxisLabel(value=marca, label=ft.Text(f"{marca}{unidad}", size=11, color=TEXTO_SEC))
            for marca in range(minimo, maximo + 1, paso)
        ],
        label_size=40,
    )

    # Grafica de linea completa con cuadricula y limites
    return fch.LineChart(
        data_series=[serie_temperatura],
        min_x=0,
        max_x=max(5, len(valores) - 1),
        min_y=minimo,
        max_y=maximo,
        expand=True,
        left_axis=eje_izquierdo,
        horizontal_grid_lines=fch.ChartGridLines(
            interval=paso,
            color=PANEL_2,
            width=1,
        ),
    )


def crear_panel_sensor(sensor):
    if sensor["visualizacion"] == "circular":
        contenido = crear_indicador_circular("Porcentaje de prueba", "—", 0, ft.Icons.SENSORS, AZUL)
        contenido.expand = None
        anillo = contenido.content.controls[1]
        progreso = anillo.controls[0]
        etiqueta = anillo.controls[1].content

        def actualizar(historial):
            progreso.value = historial[-1] / 100 if historial else 0
            etiqueta.value = f"{historial[-1]}%" if historial else "—"

    else:
        grafica = crear_grafica_linea(minimo=0, maximo=100, paso=25, unidad="")
        grafica.expand = None
        grafica.height = 110
        etiqueta = ft.Text("Sin lecturas", size=13, color=TEXTO_SEC)
        contenido = ft.Column([etiqueta, grafica], spacing=5)

        def actualizar(historial):
            etiqueta.value = f"Último valor: {historial[-1]}" if historial else "Sin lecturas"
            grafica.data_series[0].points = [
                fch.LineChartDataPoint(indice, valor)
                for indice, valor in enumerate(historial)
            ]
            grafica.max_x = max(5, len(historial) - 1)

    tarjeta = ft.Container(
        col={"xs": 12, "md": 6, "xl": 4},
        padding=12,
        border_radius=12,
        bgcolor=PANEL,
        content=ft.Column(
            [ft.Text(sensor["nombre"], color=TEXTO, size=15, weight=ft.FontWeight.BOLD), contenido],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
    )
    return tarjeta, actualizar

# Crea un indicador circular de porcentaje con valor centrado
def crear_indicador_circular(titulo, valor_texto, porcentaje, icono, color):

    # Anillo de progreso y texto de porcentaje superpuesto
    anillo_con_texto = ft.Stack(
        controls=[
            # Anillo exterior
            ft.ProgressRing(
                value=porcentaje,
                stroke_width=9,
                color=color,
                bgcolor=PANEL_2,
                stroke_cap=ft.StrokeCap.ROUND,
                width=95,
                height=95,
            ),
            # Valor porcentual en el centro
            ft.Container(
                content=ft.Text(
                    valor_texto,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=TEXTO,
                ),
                alignment=ft.Alignment(0, 0),
                width=95,
                height=95,
            ),
        ],
        alignment=ft.Alignment(0, 0),
    )

    # Contenedor de la tarjeta del medidor circular
    return ft.Container(
        content=ft.Column(
            controls=[
                # Cabecera del medidor con icono y titulo
                ft.Row(
                    controls=[
                        ft.Icon(icono, size=16, color=color),
                        ft.Text(titulo, size=14, color=TEXTO_SEC, weight=ft.FontWeight.W_500),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                ),
                # Anillo de progreso centrado
                anillo_con_texto,
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=PANEL_2,
        padding=12,
        border_radius=12,
        expand=True,
    )
