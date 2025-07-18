# pydocx_render/renderer.py
# --- VERSÃO FINAL CORRIGIDA ---

import fitz
import os
from .core.dom import Document

try:
    from .layout.line_breaker import layout_paragraph, FontMetrics
    print("INFO: Usando motor de layout Cython (otimizado).")
except ImportError:
    print("AVISO: Extensão Cython não encontrada. Usando motor de layout Python puro (mais lento).")
    from .layout.line_breaker_pure import layout_paragraph, FontMetrics

def find_font_file(style='regular'):
    """Encontra o arquivo de fonte (.ttf) para um determinado estilo."""
    font_map = {
        'regular': 'arial.ttf',
        'bold': 'arialbd.ttf',    # Arial Bold
        'italic': 'ariali.ttf',   # Arial Italic
        'bold_italic': 'arialbi.ttf' # Arial Bold Italic
    }
    font_filename = font_map.get(style, 'arial.ttf')
    
    font_path = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts", font_filename)
    
    if not os.path.exists(font_path):
        # Tenta um fallback para Liberation (comum no Linux, pode ser instalado no Windows)
        fallback_map = {
            'regular': 'LiberationSans-Regular.ttf',
            'bold': 'LiberationSans-Bold.ttf',
            'italic': 'LiberationSans-Italic.ttf',
            'bold_italic': 'LiberationSans-BoldItalic.ttf'
        }
        font_filename = fallback_map.get(style)
        font_path = f"/usr/share/fonts/truetype/liberation/{font_filename}"
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Arquivo de fonte '{font_map[style]}' ou seu fallback não encontrado.")
    
    return font_path

def render_to_pdf(doc: Document, output_path: str):
    pdf_doc = fitz.open()
    page = pdf_doc.new_page()

    page_width = page.rect.width
    margin = 50
    y_cursor = 50
    line_height = 15
    font_size = 11
    max_width = page_width - (2 * margin)
    
    try:
        # A classe de métricas precisa apenas da fonte regular para os cálculos de largura
        regular_font_file = find_font_file('regular')
        metrics = FontMetrics(regular_font_file)
    except (FileNotFoundError, TypeError) as e:
        print(f"AVISO: {e}. Recorrendo a estimativas de largura.")
        from .layout.line_breaker_pure import FontMetrics as PureMetrics
        metrics = PureMetrics()

    for para in doc.body:
        lines_of_runs = layout_paragraph(para.runs, metrics, max_width, font_size)

        for line_runs in lines_of_runs:
            if y_cursor > page.rect.height - margin:
                page = pdf_doc.new_page()
                y_cursor = margin

            x_cursor = margin
            for i, run in enumerate(line_runs):
                style = 'regular'
                if run.is_bold and run.is_italic:
                    style = 'bold_italic'
                elif run.is_bold:
                    style = 'bold'
                elif run.is_italic:
                    style = 'italic'
                
                try:
                    # Encontra o arquivo .ttf para o estilo atual
                    font_file = find_font_file(style)
                    
                    text_to_draw = (" " if i > 0 else "") + run.text
                    
                    # AQUI ESTÁ A CORREÇÃO: passamos o 'fontfile' para o PyMuPDF
                    page.insert_text(
                        (x_cursor, y_cursor),
                        text_to_draw,
                        fontname=f"F{style}", # Um nome único para a fonte no PDF
                        fontfile=font_file,
                        fontsize=font_size
                    )
                    x_cursor += metrics.get_text_width(text_to_draw, font_size)
                
                except FileNotFoundError as e:
                    print(f"ERRO DE FONTE: {e}, pulando run.")
                    continue

            y_cursor += line_height

    pdf_doc.save(output_path, garbage=4, deflate=True)
    pdf_doc.close()