# pydocx_render/layout/line_breaker_pure.py
# --- VERSÃO CORRIGIDA E MELHORADA ---

from ..core.dom import Run

class FontMetrics:
    def __init__(self, font_path=None):
        self.char_width = 7.0
    
    def get_text_width(self, text, font_size):
        return len(text) * self.char_width * (font_size / 11.0)

def layout_paragraph(paragraph_runs, metrics, max_width, font_size):
    lines = []
    current_line_runs = []
    current_line_width = 0.0
    
    # 1. Achatamos a estrutura: de uma lista de 'runs' para uma lista de 'palavras'
    all_words = []
    for run in paragraph_runs:
        for word in run.text.split(' '):
            if word:
                all_words.append(Run(text=word, is_bold=run.is_bold, is_italic=run.is_italic))

    if not all_words:
        return []

    # 2. Construímos as linhas a partir da lista de palavras
    for word_run in all_words:
        # Calcula a largura da palavra + um espaço antes (se não for a primeira palavra da linha)
        word_text_with_space = (" " if current_line_runs else "") + word_run.text
        word_width = metrics.get_text_width(word_text_with_space, font_size)

        if current_line_width + word_width <= max_width:
            current_line_runs.append(word_run)
            current_line_width += word_width
        else:
            if current_line_runs:
                lines.append(current_line_runs)
            
            current_line_runs = [word_run]
            current_line_width = metrics.get_text_width(word_run.text, font_size)

    if current_line_runs:
        lines.append(current_line_runs)

    return lines