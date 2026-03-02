from openpyxl import Workbook

def create_analysis_excel(analysis: dict) -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = "Análisis"

    # Cabeceras
    ws.append(["Palabra", "Cantidad"])

    # Datos
    for palabra, cantidad in analysis.items():
        ws.append([palabra, cantidad])

    file_path = "analysis_result.xlsx"
    wb.save(file_path)

    return file_path
