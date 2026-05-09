import io
import base64
from fpdf import FPDF
import tempfile
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 15)
        self.cell(0, 10, "Reporte de Optimización - Método Gráfico", border=False, ln=1, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

def generar_pdf_grafico(problema: dict, resultados: dict) -> bytes:
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    # Título y Descripción
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, f"Problema: {problema.get('titulo', 'Sin título')}", ln=1)
    pdf.set_font("helvetica", size=12)
    if problema.get("descripcion"):
        pdf.multi_cell(0, 10, f"Descripción: {problema['descripcion']}")
    pdf.ln(5)

    # Función Objetivo
    fo = problema["funcion_objetivo"]
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Función Objetivo:", ln=1)
    pdf.set_font("helvetica", size=12)
    tipo_str = fo.get("tipo", "max").upper()
    pdf.cell(0, 10, f"{tipo_str} Z = {fo.get('x', 0)}x + {fo.get('y', 0)}y", ln=1)
    pdf.ln(5)

    # Restricciones
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Restricciones:", ln=1)
    pdf.set_font("helvetica", size=12)
    for r in problema.get("restricciones", []):
        x_val = r.get("x", 0)
        y_val = r.get("y", 0)
        signo = r.get("signo", "<=")
        valor = r.get("valor", 0)
        glosa = f" ({r['glosa']})" if r.get("glosa") else ""
        pdf.cell(0, 8, f"{x_val}x + {y_val}y {signo} {valor}{glosa}", ln=1)
    pdf.ln(5)

    # Resultados y Gráfico
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Solución Óptima", ln=1)
    pdf.set_font("helvetica", size=12)
    
    # El mensaje de la solución (ej: "La solución óptima es: 50 x y 40 y ...")
    mensaje = resultados.get("mensaje", "")
    pdf.multi_cell(0, 8, mensaje)
    pdf.ln(5)

    # Valores de la FO en cada vértice
    valores_fo = resultados.get("valores_fo", [])
    if valores_fo:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "Evaluación en vértices:", ln=1)
        pdf.set_font("helvetica", size=11)
        for v in valores_fo:
            pdf.cell(0, 7, f"  {v}", ln=1)
        pdf.ln(5)

    # Extraer imagen base64 (el algoritmo gráfico usa 'img')
    grafico_b64 = resultados.get("img") or resultados.get("grafico_base64") or ""
    if grafico_b64:
        try:
            image_data = base64.b64decode(grafico_b64)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                tmp_file.write(image_data)
                tmp_file_path = tmp_file.name

            # Nueva página dedicada al gráfico
            pdf.add_page()
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "Gráfico de la Región Factible", ln=1, align="C")
            pdf.ln(5)

            # Centrar imagen: ancho de página = 210, márgenes = 10 cada lado
            img_w = 190
            img_x = (210 - img_w) / 2
            pdf.image(tmp_file_path, x=img_x, w=img_w)
            os.remove(tmp_file_path)
        except Exception as e:
            pdf.cell(0, 10, f"Error al generar gráfico: {str(e)}", ln=1)

    # Devolver PDF como bytes
    return bytes(pdf.output())

