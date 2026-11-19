import flet as ft
import flet_charts as fch
from ui.estilos import AZUL, AMARILLO, PANEL_2, TEXTO, TEXTO_SEC

# Genera la grafica de linea para la temperatura
def crear_grafica_temperatura():

    # Serie de datos con los puntos de temperatura y puntos visibles
    serie_temperatura = fch.LineChartData(
        points=[
            fch.LineChartDataPoint(0, 24.8),
            fch.LineChartDataPoint(1, 25.1),
            fch.LineChartDataPoint(2, 25.4),
            fch.LineChartDataPoint(3, 25.2),
            fch.LineChartDataPoint(4, 25.8),
            fch.LineChartDataPoint(5, 25.5),
        ],
        color=AZUL,
        stroke_width=3,
        curved=True,
        point=True,
    )

    # Configuracion de ejes con valores de temperatura
    eje_izquierdo = fch.ChartAxis(
        labels=[
            fch.ChartAxisLabel(value=20, label=ft.Text("20°C", size=11, color=TEXTO_SEC)),
            fch.ChartAxisLabel(value=25, label=ft.Text("25°C", size=11, color=TEXTO_SEC)),
            fch.ChartAxisLabel(value=30, label=ft.Text("30°C", size=11, color=TEXTO_SEC)),
            fch.ChartAxisLabel(value=35, label=ft.Text("35°C", size=11, color=TEXTO_SEC)),
            fch.ChartAxisLabel(value=40, label=ft.Text("40°C", size=11, color=TEXTO_SEC)),
        ],
        label_size=40,
    )

    # Grafica de linea completa con cuadricula y limites
    return fch.LineChart(
        data_series=[serie_temperatura],
        min_x=0,
        max_x=5,
        min_y=20,
        max_y=40,
        expand=True,
        left_axis=eje_izquierdo,
        horizontal_grid_lines=fch.ChartGridLines(
            interval=5,
            color=PANEL_2,
            width=1,
        ),
    )

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