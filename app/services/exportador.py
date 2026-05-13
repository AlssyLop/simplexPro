import io
import base64
from fpdf import FPDF
import tempfile
import os
from app.schemas.grafico_model import MostrarResultadoGrafico

class PDFReport(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 15)
        self.cell(0, 10, "Reporte de Optimización - Método Gráfico", border=False, ln=1, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

def generar_pdf_grafico(resultado: MostrarResultadoGrafico) -> bytes:
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
   
    # Título y Descripción
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, f"Problema: {resultado.titulo}", ln=1)
    pdf.set_font("helvetica", size=12)
    if resultado.descripcion:
        pdf.multi_cell(0, 10, f"Descripción: {resultado.descripcion}")
    pdf.ln(5)

    # Función Objetivo
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Función Objetivo:", ln=1)
    pdf.set_font("helvetica", size=12)
    pdf.cell(0, 10, resultado.funcion_objetivo, ln=1)
    pdf.ln(5)

    # Restricciones
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Restricciones:", ln=1)
    pdf.set_font("helvetica", size=12)
    for r in resultado.restricciones:
        pdf.cell(0, 6, f"{r.inecuacion} - {r.glosa}", ln=1)
    pdf.ln(5)
    
    # --- Nueva página: Solución y Gráfico ---
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Solución Óptima", ln=1)
    pdf.set_font("helvetica", size=12)
    
    # El mensaje de la solución
    pdf.multi_cell(0, 6, resultado.mensaje)
    pdf.ln(5)

    # Valores de la FO en cada vértice
    if resultado.valoresFO:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "Evaluación en vértices:", ln=1)
        pdf.set_font("helvetica", size=11)
        for v in resultado.valoresFO:
            pdf.cell(0, 7, f"  {v}", ln=1)
        pdf.ln(5)
    # Insertar imagen
    if resultado.grafico:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                tmp_file.write(base64.b64decode(resultado.grafico))
                tmp_file_path = tmp_file.name

            pdf.ln(5)
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "Gráfico de la Región Factible", ln=1, align="C")
            pdf.ln(5)

            img_w = 190
            img_x = (210 - img_w) / 2
            pdf.image(tmp_file_path, x=img_x, w=img_w)
            os.remove(tmp_file_path)
        except Exception as e:
            pdf.cell(0, 10, f"Error al generar gráfico: {str(e)}", ln=1)

    # Devolver PDF como bytes
    return bytes(pdf.output())

