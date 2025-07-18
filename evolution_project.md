## **PyDocX-Render - Documento de Evolução e Estado Atual**

**Versão:** 0.1.0
**Data:** 24 de maio de 2024
**Status:** Núcleo funcional com suporte a texto, estilos (negrito/itálico) e quebra de linha otimizada com Cython.

### **1. Resumo do Projeto**

O `PyDocX-Render` é um SDK (Software Development Kit) desenvolvido em Python com o objetivo de converter documentos no formato `.docx` para PDF com alta fidelidade. Para alcançar a performance necessária para um motor de layout complexo, o projeto utiliza Cython para compilar as partes críticas de cálculo para código C nativo, enquanto mantém a flexibilidade e o ecossistema do Python para a lógica de alto nível.

### **2. Jornada de Desenvolvimento e Depuração (Histórico de Evolução)**

O desenvolvimento seguiu uma abordagem iterativa, enfrentando e resolvendo desafios em camadas:

1.  **Estruturação Inicial:** O projeto foi iniciado com uma estrutura de pastas clara (`core`, `layout`, `renderer`) e um script de setup (`setup_project.py`) para automatizar a criação do ambiente, arquivos e dependências.

2.  **Parser e Renderizador Básico (Prova de Conceito):** A primeira versão funcional conseguia:
    *   Analisar (`parse`) um arquivo `.docx`, extraindo o texto de cada parágrafo.
    *   Renderizar este texto em um PDF, mas com uma limitação crítica: cada parágrafo era desenhado como uma única linha, ignorando as margens da página e qualquer formatação.
    *   **Resultado:** Validamos que a leitura do DOCX e a escrita do PDF eram possíveis.

3.  **Introdução do Motor de Layout Cython:**
    *   Foi criado o `line_breaker.pyx`, contendo um motor de layout para calcular a quebra de linhas.
    *   O `renderer.py` foi atualizado para usar este motor.
    *   **Desafio Encontrado:** A compilação de Cython no Windows provou ser complexa, exigindo o Microsoft C++ Build Tools. Criamos o `fix_cython.py` para diagnosticar e ajudar a resolver esses problemas de ambiente.

4.  **Depuração de Interoperabilidade (Python <> Cython):**
    *   **Erro 1: `'Run' is not a type identifier`**. Resolvemos aprendendo que variáveis que contêm objetos Python puros (como nossa classe `Run`) não devem ser declaradas com `cdef` dentro de funções Cython.
    *   **Erro 2: `AttributeError: 'FontMetrics' object has no attribute 'get_text_width'`**. Resolvemos aprendendo sobre a visibilidade de métodos em Cython. Trocamos `@cython.cfunc` por `cpdef`, que cria uma "ponte" para que o método C otimizado seja visível e chamável pelo código Python puro.
    *   **Erro 3 (Sintaxe): `Return type annotation is not allowed...`**. Corrigimos a assinatura da função `cpdef` para usar a sintaxe de estilo C (`cpdef float nome_funcao(...)`) em vez da sintaxe de anotação Python (`-> float`).

5.  **Depuração da Lógica da Biblioteca (PyMuPDF):**
    *   **Erro Final: `Exception: need font file or buffer`**. Após resolver todos os problemas de compilação, encontramos um erro de tempo de execução. O PyMuPDF exigia o arquivo de fonte (`.ttf`) real para estilos como negrito e itálico.
    *   **Solução:** Refatoramos o `renderer.py` para encontrar os arquivos de fonte corretos (`arialbd.ttf`, `ariali.ttf`, etc.) e fornecê-los ao PyMuPDF, resolvendo o problema e alcançando o resultado final desejado.

### **3. Estado Atual dos Arquivos do Projeto**

Aqui estão as versões finais e funcionais de todos os arquivos do projeto, refletindo todas as correções e melhorias que fizemos.

---
#### **`setup.py`**
```python
# setup.py
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

# Definimos nossa extensao Cython
extensions = [
    Extension(
        "pydocx_render.layout.line_breaker",
        ["pydocx_render/layout/line_breaker.pyx"],
        include_dirs=[numpy.get_include()]
    ),
]

setup(
    name="PyDocX-Render",
    ext_modules=cythonize(extensions),
    zip_safe=False,
)
```
---
#### **`pydocx_render/core/dom.py`**
```python
# pydocx_render/core/dom.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class Run:
    """Um trecho de texto com a mesma formatação."""
    text: str
    is_bold: bool = False
    is_italic: bool = False

@dataclass
class Paragraph:
    """Um parágrafo, contendo uma ou mais Runs."""
    runs: List[Run] = field(default_factory=list)
    # Futuro: alignment: str = 'left'

@dataclass
class Document:
    """O documento inteiro, contendo uma lista de Parágrafos."""
    body: List[Paragraph] = field(default_factory=list)
```
---
#### **`pydocx_render/core/parser.py`**
```python
# pydocx_render/core/parser.py
import zipfile
from lxml import etree
from .dom import Document, Paragraph, Run

NSMAP = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def parse_docx(file_path: str) -> Document:
    """Analisa um arquivo .docx e retorna nosso objeto DOM."""
    doc = Document()

    with zipfile.ZipFile(file_path, 'r') as docx_zip:
        xml_content = docx_zip.read('word/document.xml')
        root = etree.fromstring(xml_content)
        body = root.find('w:body', NSMAP)

        for p_node in body.findall('w:p', NSMAP):
            para = Paragraph()
            # Futuro: Ler o alinhamento aqui de p_node.find('.//w:jc', NSMAP)
            
            for r_node in p_node.findall('w:r', NSMAP):
                text_node = r_node.find('w:t', NSMAP)
                if text_node is not None:
                    # Preserve espaços (importante para formatação)
                    text = text_node.text or ""
                    if text_node.get('{http://www.w3.org/XML/1998/namespace}space') == 'preserve':
                        pass # O texto já está correto

                    is_bold = r_node.find('.//w:b', NSMAP) is not None
                    is_italic = r_node.find('.//w:i', NSMAP) is not None
                    para.runs.append(Run(text=text, is_bold=is_bold, is_italic=is_italic))
            
            if para.runs:
                doc.body.append(para)

    return doc
```
---
#### **`pydocx_render/layout/line_breaker.pyx`**
```cython
# pydocx_render/layout/line_breaker.pyx
# distutils: language=c++

cimport cython
import freetype
from ..core.dom import Run

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

# Lógica de layout que aceita uma lista de Runs
def layout_paragraph(list paragraph_runs, FontMetrics metrics, float max_width, int font_size):
    cdef list lines = []
    cdef list current_line_runs = []
    cdef float current_line_width = 0.0
    
    # 1. Achatamos a estrutura: de uma lista de 'runs' para uma lista de 'palavras'
    all_words = []
    for run in paragraph_runs:
        # Usamos split() que lida com múltiplos espaços e os remove
        for word in run.text.split():
            if word:
                all_words.append(Run(text=word, is_bold=run.is_bold, is_italic=run.is_italic))

    if not all_words:
        return []

    # 2. Construímos as linhas a partir da lista de palavras
    for word_run in all_words:
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
```
---
#### **`pydocx_render/layout/line_breaker_pure.py`**
```python
# pydocx_render/layout/line_breaker_pure.py
# Versão Python pura do motor de layout que suporta estilos

from ..core.dom import Run

class FontMetrics:
    """Métricas de fonte usando estimativas"""
    def __init__(self, font_path=None):
        self.char_width = 7.0
    
    def get_text_width(self, text, font_size):
        return len(text) * self.char_width * (font_size / 11.0)

def layout_paragraph(paragraph_runs, metrics, max_width, font_size):
    lines = []
    current_line_runs = []
    current_line_width = 0.0
    
    all_words = []
    for run in paragraph_runs:
        for word in run.text.split():
            if word:
                all_words.append(Run(text=word, is_bold=run.is_bold, is_italic=run.is_italic))

    if not all_words:
        return []

    for word_run in all_words:
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
```
---
#### **`pydocx_render/renderer.py`**
```python
# pydocx_render/renderer.py
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
        'bold': 'arialbd.ttf',
        'italic': 'ariali.ttf',
        'bold_italic': 'arialbi.ttf'
    }
    font_filename = font_map.get(style, 'arial.ttf')
    
    font_path = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts", font_filename)
    
    if not os.path.exists(font_path):
        # Lógica de fallback pode ser adicionada aqui para Linux/macOS
        raise FileNotFoundError(f"Arquivo de fonte '{font_filename}' não encontrado em C:\\Windows\\Fonts.")
    
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
        regular_font_file = find_font_file('regular')
        metrics = FontMetrics(regular_font_file)
    except (FileNotFoundError, TypeError) as e:
        print(f"AVISO: {e}. Recorrendo a estimativas de largura de fonte.")
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
                    font_file = find_font_file(style)
                    text_to_draw = (" " if i > 0 else "") + run.text
                    
                    page.insert_text(
                        (x_cursor, y_cursor),
                        text_to_draw,
                        fontname=f"F-{style}",
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
```
---
#### **`main.py`**
```python
# main.py
from pydocx_render.core.parser import parse_docx
from pydocx_render.renderer import render_to_pdf
import os

def main():
    input_file = "documents/simple_text.docx"
    output_file = "output/result.pdf"

    if not os.path.exists(input_file):
        print(f"ERRO: Arquivo de entrada '{input_file}' não encontrado.")
        print("Certifique-se de que o script 'setup_project.py' foi executado.")
        return

    print(f"Parsing '{input_file}'...")
    dom = parse_docx(input_file)
    print("DOM criado com sucesso.")

    print(f"Rendering to '{output_file}'...")
    render_to_pdf(dom, output_file)
    print("PDF gerado com sucesso!")

if __name__ == "__main__":
    main()
```
---
### **4. Próximos Passos (Roteiro Futuro)**

Com o núcleo do SDK estabilizado, podemos agora adicionar novos recursos de forma segura.

1.  **[RECOMENDADO] Suporte a Alinhamento de Parágrafo:**
    *   **Objetivo:** Fazer com que parágrafos possam ser alinhados ao centro, à direita ou justificados.
    *   **Passos:**
        1.  **DOM:** Adicionar `alignment: str = 'left'` à classe `Paragraph`.
        2.  **Parser:** No `parser.py`, ler a tag `<w:jc w:val="..."/>` dentro das propriedades do parágrafo (`w:pPr`).
        3.  **Renderizador:** No `renderer.py`, para cada linha, calcular sua largura total. Antes de desenhar os `runs` da linha, calcular o `x_cursor` inicial com base no alinhamento.
            *   `center`: `x_start = margin + (max_width - line_width) / 2`
            *   `right`: `x_start = margin + max_width - line_width`
            *   `justify`: Este é avançado, envolveria ajustar o espaçamento entre as palavras. Podemos começar com os outros três.

2.  **Suporte a Tamanho e Cor da Fonte:**
    *   **Objetivo:** Permitir que diferentes trechos de texto tenham tamanhos e cores diferentes.
    *   **Passos:** Isso exigirá modificações mais profundas no motor de layout para lidar com alturas e larguras variáveis dentro da mesma linha.

3.  **Testes Unitários:**
    *   **Objetivo:** Criar um conjunto de testes usando `pytest` ou `unittest` para garantir que futuras mudanças não quebrem a funcionalidade existente.
    *   **Passos:** Criar testes para o `parser` (dado um XML, o DOM é criado corretamente?) e para o `layout` (dada uma lista de runs, as linhas são quebradas corretamente?).

A implementação do **Alinhamento de Parágrafo** é o próximo passo lógico e mais gratificante. Ele solidificará ainda mais a estrutura do nosso renderizador.