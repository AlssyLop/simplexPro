import io
import base64
from fpdf import FPDF
import tempfile
import os
import urllib.request
import unicodedata
from app.schemas.resultados import MostrarResultadoGrafico

def sanitizar_texto(texto: str) -> str:
    if not texto:
        return ""
    
    reemplazos = {
        "ı": "i",
        "≤": "<=",
        "≥": ">=",
        "≠": "!=",
        "→": "->",
        "←": "<-",
        "−": "-",
        "×": "*",
        "÷": "/",
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
    }
    
    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)
        
    try:
        texto.encode("cp1252")
    except UnicodeEncodeError:
        caracteres_validos = []
        for c in texto:
            try:
                c.encode("cp1252")
                caracteres_validos.append(c)
            except UnicodeEncodeError:
                normalized = unicodedata.normalize("NFKD", c)
                try:
                    normalized.encode("cp1252")
                    caracteres_validos.append(normalized)
                except UnicodeEncodeError:
                    caracteres_validos.append("?")
        texto = "".join(caracteres_validos)
        
    return texto

def limpiar_texto(texto: str, font_family: str) -> str:
    if not texto:
        return ""
    if font_family == "helvetica":
        return sanitizar_texto(texto)
    return texto

def cargar_fuente_unicode(pdf: FPDF) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fonts_dir = os.path.join(base_dir, "assets", "fonts")
    
    os.makedirs(fonts_dir, exist_ok=True)
    
    regular_path = os.path.join(fonts_dir, "Roboto-Regular.ttf")
    bold_path = os.path.join(fonts_dir, "Roboto-Bold.ttf")
    italic_path = os.path.join(fonts_dir, "Roboto-Italic.ttf")
    
    try:
        pdf.add_font("Roboto", "", regular_path)
        pdf.add_font("Roboto", "B", bold_path)
        pdf.add_font("Roboto", "I", italic_path)
        return "Roboto"
    except Exception:
        return "helvetica"

class PDFReport(FPDF):
    def __init__(self, font_family="helvetica", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font_family_custom = font_family

    def header(self):
        self.set_font(self.font_family_custom, "B", 15)
        titulo = limpiar_texto("Reporte de Optimización - Método Gráfico", self.font_family_custom)
        self.cell(0, 10, titulo, border=False, ln=1, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_family_custom, "I", 8)
        texto_footer = limpiar_texto(f"Página {self.page_no()}", self.font_family_custom)
        self.cell(0, 10, texto_footer, align="C")

def generar_pdf_grafico(resultado: MostrarResultadoGrafico) -> bytes:
    pdf = PDFReport()
    try:
        font_family = cargar_fuente_unicode(pdf)
    except Exception:
        font_family = "helvetica"
        
    pdf.font_family_custom = font_family
    
    pdf.add_page()
    pdf.set_font(font_family, size=12)
   
    # Título y Descripción
    pdf.set_font(font_family, "B", 14)
    pdf.cell(0, 10, limpiar_texto(f"Problema: {resultado.titulo}", font_family), ln=1)
    pdf.set_font(font_family, size=12)
    if resultado.descripcion:
        pdf.multi_cell(0, 10, limpiar_texto(f"Descripción: {resultado.descripcion}", font_family))
    pdf.ln(5)

    # Función Objetivo
    pdf.set_font(font_family, "B", 12)
    pdf.cell(0, 10, limpiar_texto("Función Objetivo:", font_family), ln=1)
    pdf.set_font(font_family, size=12)
    pdf.cell(0, 10, limpiar_texto(resultado.funcion_objetivo, font_family), ln=1)
    pdf.ln(5)

    # Restricciones
    pdf.set_font(font_family, "B", 12)
    pdf.cell(0, 10, limpiar_texto("Restricciones:", font_family), ln=1)
    pdf.set_font(font_family, size=12)
    for r in resultado.restricciones:
        texto_r = f"{r.inecuacion}  {r.glosa if r.glosa else ''}"
        pdf.cell(0, 6, limpiar_texto(texto_r, font_family), ln=1)
    pdf.ln(5)
    
    # --- Nueva página: Solución y Gráfico ---
    pdf.add_page()
    pdf.set_font(font_family, "B", 14)
    pdf.cell(0, 10, limpiar_texto("Solución Óptima", font_family), ln=1)
    pdf.set_font(font_family, size=12)
    
    # El mensaje de la solución
    pdf.multi_cell(0, 6, limpiar_texto(resultado.mensaje, font_family))
    pdf.ln(5)

    # Valores de la FO en cada vértice
    if resultado.valoresFO:
        pdf.set_font(font_family, "B", 12)
        pdf.cell(0, 10, limpiar_texto("Evaluación en vértices:", font_family), ln=1)
        pdf.set_font(font_family, size=11)
        for v in resultado.valoresFO:
            pdf.cell(0, 7, limpiar_texto(f"  {v}", font_family), ln=1)
        pdf.ln(5)
        
    # Insertar imagen
    if resultado.grafico:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                tmp_file.write(base64.b64decode(resultado.grafico))
                tmp_file_path = tmp_file.name

            pdf.ln(5)
            pdf.set_font(font_family, "B", 14)
            pdf.cell(0, 10, limpiar_texto("Gráfico de la Región Factible", font_family), ln=1, align="C")
            pdf.ln(5)

            img_w = 190
            img_x = (210 - img_w) / 2
            pdf.image(tmp_file_path, x=img_x, w=img_w)
            os.remove(tmp_file_path)
        except Exception as e:
            msg_error = limpiar_texto(f"Error al generar gráfico: {str(e)}", font_family)
            pdf.cell(0, 10, msg_error, ln=1)

    # Devolver PDF como bytes
    return bytes(pdf.output())
