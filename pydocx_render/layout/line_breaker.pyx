# pydocx_render/layout/line_breaker.pyx
# -*- coding: utf-8 -*-
# Versão simplificada sem freetype para evitar problemas de compilação

# pydocx_render/layout/line_breaker.pyx
# --- NOVO CONTEÚDO ---
# distutils: language=c++

# pydocx_render/layout/line_breaker.pyx
# --- VERSÃO CORRIGIDA E MELHORADA ---
# distutils: language=c++

cimport cython
import freetype
from ..core.dom import Run

# ... (imports e __init__ da classe) ...
cdef class FontMetrics:
    cdef face
    
    def __init__(self, font_path):
        print(f"DEBUG: FontMetrics (Cython) inicializado com path: {font_path}")
        self.face = freetype.Face(font_path)

    # Assinatura corrigida: tipo de retorno ANTES do nome.
    # Tipos de argumento DENTRO dos parênteses.
    cpdef float get_text_width(self, str text, int font_size):
        self.face.set_char_size(font_size * 64)
        cdef float width = 0.0
        for char_code in text:
            self.face.load_char(char_code)
            width += self.face.glyph.advance.x
        return width / 64.0

# --- LÓGICA DE LAYOUT CORRIGIDA ---
def layout_paragraph(list paragraph_runs, FontMetrics metrics, float max_width, int font_size):
    cdef list lines = []
    cdef list current_line_runs = []
    cdef float current_line_width = 0.0
       
    # Primeiro, criamos uma lista única de "palavras" com seus estilos
    all_words = []
    for run in paragraph_runs:
        for word in run.text.split(' '):
            if word:
                # Cada palavra herda o estilo de seu 'run' original
                all_words.append(Run(text=word, is_bold=run.is_bold, is_italic=run.is_italic))
    
    if not all_words:
        return []

    # Agora, processamos a lista de palavras para formar as linhas
    for word_run in all_words:
        # Adicionamos um espaço para o cálculo da largura, exceto na primeira palavra da linha
        word_text_with_space = (" " if current_line_runs else "") + word_run.text
        word_width = metrics.get_text_width(word_text_with_space, font_size)

        if current_line_width + word_width <= max_width:
            # A palavra cabe, adicionamos à linha atual
            current_line_runs.append(word_run)
            current_line_width += word_width
        else:
            # A palavra não cabe, finalizamos a linha atual
            if current_line_runs:
                lines.append(current_line_runs)
            
            # E começamos uma nova linha com a palavra atual
            current_line_runs = [word_run]
            current_line_width = metrics.get_text_width(word_run.text, font_size)

    if current_line_runs:
        lines.append(current_line_runs)

    return lines