from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.chart import BarChart, Reference

def create_analysis_excel(analysis: dict) -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = "Análisis"

    todas_las_palabras = set()
    for item in analysis:
        palabras_dict = item.get('palabras', {})
        todas_las_palabras.update(palabras_dict.keys())
    
    lista_palabras = sorted(list(todas_las_palabras))

    headers = ["Archivo Audio"] + lista_palabras + ["Pregunta Realizada", "Resultado de Búsqueda"]
    ws.append(headers)

    header_fill = PatternFill(start_color="CFE2F3", end_color="CFE2F3", fill_type="solid")
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = header_fill

    for item in analysis:
        fila = [item.get('audio', 'N/A')]
        
        conteo_actual = item.get('palabras', {})
        for palabra in lista_palabras:
            fila.append(conteo_actual.get(palabra, 0))
        
        busqueda = item.get('busqueda', {})
        fila.append(busqueda.get('texto', 'Sin consulta'))
        fila.append(busqueda.get('detalle', 'N/A'))
        
        ws.append(fila)

    ws.column_dimensions['A'].width = 25
    ult_col_idx = len(headers)
    from openpyxl.utils import get_column_letter
    ws.column_dimensions[get_column_letter(ult_col_idx)].width = 50
    
    ws_charts = wb.create_sheet(title="Gráficos")
    ws_charts.append(["Palabra", "Total"]) # Fila 1
    
    totales = {}
    for item in analysis:
        for palabra, cantidad in item.get('palabras', {}).items():
            totales[palabra] = totales.get(palabra, 0) + cantidad
            
    for i, (palabra, total) in enumerate(totales.items(), start=2):
        ws_charts.cell(row=i, column=1, value=palabra)
        ws_charts.cell(row=i, column=2, value=total)

    chart = BarChart()
    chart.type = "col"
    chart.style = 10
    chart.title = "Total de Palabras Clave"
    chart.y_axis.title = 'Cantidad'
    chart.x_axis.title = 'Palabras'
    chart.legend = None

    data = Reference(ws_charts, min_col=2, min_row=1, max_row=len(totales) + 1, max_col=2)
    cats = Reference(ws_charts, min_col=1, min_row=2, max_row=len(totales) + 1)

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    
    ws_charts.add_chart(chart, "D2")

    file_path = "analysis_result.xlsx"
    wb.save(file_path)

    return file_path
