import flet as ft

# Tabla para mostrar el historial de lecturas de sensores
def crear_tabla_lecturas():
    return ft.DataTable(
        # Definicion de columnas
        columns=[
            ft.DataColumn(ft.Text("Hora")),
            ft.DataColumn(ft.Text("Temperatura")),
            ft.DataColumn(ft.Text("Humedad")),
            ft.DataColumn(ft.Text("Luz")),
        ],
        # Filas con los datos de cada lectura
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("20:34:10")),
                ft.DataCell(ft.Text("25.4 °C")),
                ft.DataCell(ft.Text("62 %")),
                ft.DataCell(ft.Text("80 %")),
            ]),
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("20:34:07")),
                ft.DataCell(ft.Text("25.3 °C")),
                ft.DataCell(ft.Text("62 %")),
                ft.DataCell(ft.Text("80 %")),
            ]),
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("20:34:04")),
                ft.DataCell(ft.Text("25.3 °C")),
                ft.DataCell(ft.Text("61 %")),
                ft.DataCell(ft.Text("79 %")),
            ]),
        ],
    )
