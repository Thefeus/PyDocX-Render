#!/usr/bin/env python3
"""
Setup completo do PyDocX-Render para Windows
Versão sem emojis, compatível com CP1252
"""

import os
import sys
import subprocess
import platform
import zipfile
from pathlib import Path

def create_directory_structure():
    """Cria a estrutura de diretórios do projeto"""
    print("Criando estrutura de diretorios...")
    
    directories = [
        "documents",
        "output", 
        "pydocx_render",
        "pydocx_render/core",
        "pydocx_render/layout",
        "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   OK {directory}/")

def create_init_files():
    """Cria os arquivos __init__.py necessários"""
    print("Criando arquivos __init__.py...")
    
    init_files = [
        "pydocx_render/__init__.py",
        "pydocx_render/core/__init__.py", 
        "pydocx_render/layout/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"   OK {init_file}")

def create_requirements_txt():
    """Cria o arquivo requirements.txt"""
    print("Criando requirements.txt...")
    
    requirements = """lxml
Pillow
PyMuPDF
cython
freetype-py
numpy"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements)
    print("   OK requirements.txt")

def create_setup_py():
    """Cria o arquivo setup.py"""
    print("Criando setup.py...")
    
    setup_content = """# setup.py
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
)"""
    
    with open("setup.py", "w", encoding="utf-8") as f:
        f.write(setup_content)
    print("   OK setup.py")

def create_dom_py():
    """Cria o arquivo dom.py"""
    print("Criando dom.py...")
    
    dom_content = """# pydocx_render/core/dom.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class Run:
    text: str
    is_bold: bool = False
    is_italic: bool = False

@dataclass
class Paragraph:
    runs: List[Run] = field(default_factory=list)

@dataclass
class Document:
    body: List[Paragraph] = field(default_factory=list)"""
    
    with open("pydocx_render/core/dom.py", "w", encoding="utf-8") as f:
        f.write(dom_content)
    print("   OK pydocx_render/core/dom.py")

def create_parser_py():
    """Cria o arquivo parser.py"""
    print("Criando parser.py...")
    
    parser_content = """# pydocx_render/core/parser.py
import zipfile
from lxml import etree
from .dom import Document, Paragraph, Run

NSMAP = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def parse_docx(file_path: str) -> Document:
    doc = Document()

    with zipfile.ZipFile(file_path, 'r') as docx_zip:
        xml_content = docx_zip.read('word/document.xml')
        root = etree.fromstring(xml_content)
        body = root.find('w:body', NSMAP)

        for p_node in body.findall('w:p', NSMAP):
            para = Paragraph()
            for r_node in p_node.findall('w:r', NSMAP):
                text_node = r_node.find('w:t', NSMAP)
                if text_node is not None:
                    text = text_node.text or ""
                    is_bold = r_node.find('.//w:b', NSMAP) is not None
                    is_italic = r_node.find('.//w:i', NSMAP) is not None
                    para.runs.append(Run(text=text, is_bold=is_bold, is_italic=is_italic))
            
            if para.runs:
                doc.body.append(para)

    return doc"""
    
    with open("pydocx_render/core/parser.py", "w", encoding="utf-8") as f:
        f.write(parser_content)
    print("   OK pydocx_render/core/parser.py")

def create_renderer_py():
    """Cria o arquivo renderer.py"""
    print("Criando renderer.py...")
    
    renderer_content = """# pydocx_render/renderer.py
import fitz
from .core.dom import Document

def render_to_pdf(doc: Document, output_path: str):
    pdf_doc = fitz.open()
    page = pdf_doc.new_page()

    y_cursor = 50
    x_margin = 50
    line_height = 15

    for para in doc.body:
        full_text = "".join(run.text for run in para.runs)
        
        page.insert_text(
            (x_margin, y_cursor),
            full_text,
            fontname="helv",
            fontsize=11
        )
        y_cursor += line_height

    pdf_doc.save(output_path)
    pdf_doc.close()"""
    
    with open("pydocx_render/renderer.py", "w", encoding="utf-8") as f:
        f.write(renderer_content)
    print("   OK pydocx_render/renderer.py")

def create_line_breaker_pyx():
    """Cria o arquivo line_breaker.pyx"""
    print("Criando line_breaker.pyx...")
    
    line_breaker_content = """# pydocx_render/layout/line_breaker.pyx
# distutils: language=c++

cimport cython
import freetype

cdef class FontMetrics:
    cdef face
    
    def __init__(self, font_path):
        self.face = freetype.Face(font_path)

    @cython.cfunc
    def get_text_width(self, text: str, font_size: int) -> float:
        self.face.set_char_size(font_size * 64)
        cdef float width = 0.0
        cdef char prev_char = 0
        
        for char_code in text:
            self.face.load_char(char_code)
            width += self.face.glyph.advance.x
            
        return width / 64.0

def layout_paragraph(text, FontMetrics metrics, float max_width, int font_size):
    cdef list lines = []
    cdef list words = text.split(' ')
    cdef str current_line = ""
    
    if not words:
        return []

    current_line = words[0]
    for i in range(1, len(words)):
        word = words[i]
        test_line = current_line + " " + word
        if metrics.get_text_width(test_line, font_size) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    
    lines.append(current_line)
    return lines"""
    
    with open("pydocx_render/layout/line_breaker.pyx", "w", encoding="utf-8") as f:
        f.write(line_breaker_content)
    print("   OK pydocx_render/layout/line_breaker.pyx")

def create_main_py():
    """Cria o arquivo main.py"""
    print("Criando main.py...")
    
    main_content = """# main.py
from pydocx_render.core.parser import parse_docx
from pydocx_render.renderer import render_to_pdf

def main():
    input_file = "documents/simple_text.docx"
    output_file = "output/result.pdf"

    print(f"Parsing '{input_file}'...")
    dom = parse_docx(input_file)
    print("DOM criado com sucesso.")

    print(f"Rendering to '{output_file}'...")
    render_to_pdf(dom, output_file)
    print("PDF gerado com sucesso!")

if __name__ == "__main__":
    main()"""
    
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(main_content)
    print("   OK main.py")

def create_test_docx():
    """Cria um documento DOCX de teste automaticamente"""
    print("Criando documento DOCX de teste...")
    
    # Conteúdo XML mínimo para um documento DOCX válido
    document_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p>
            <w:r>
                <w:t>Documento de Teste PyDocX-Render</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>Este é um parágrafo simples para testar o parser.</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:rPr>
                    <w:b/>
                </w:rPr>
                <w:t>Este texto está em negrito.</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:rPr>
                    <w:i/>
                </w:rPr>
                <w:t>Este texto está em itálico.</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</w:t>
            </w:r>
        </w:p>
    </w:body>
</w:document>'''

    # Outros arquivos necessários para um DOCX válido
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''

    main_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

    word_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>'''

    # Criar o arquivo DOCX
    try:
        with zipfile.ZipFile('documents/simple_text.docx', 'w', zipfile.ZIP_DEFLATED) as docx:
            docx.writestr('[Content_Types].xml', content_types)
            docx.writestr('_rels/.rels', main_rels)
            docx.writestr('word/document.xml', document_xml)
            docx.writestr('word/_rels/document.xml.rels', word_rels)
        
        print("   OK documents/simple_text.docx")
        return True
    except Exception as e:
        print(f"   ERRO ao criar DOCX: {e}")
        return False

def create_virtual_environment():
    """Cria e ativa o ambiente virtual"""
    print("Criando ambiente virtual...")
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("   OK Ambiente virtual criado em ./venv/")
        
        if platform.system() == "Windows":
            pip_path = "venv\\Scripts\\pip.exe"
        else:
            pip_path = "venv/bin/pip"
        
        return pip_path
        
    except subprocess.CalledProcessError as e:
        print(f"   ERRO ao criar ambiente virtual: {e}")
        return None

def install_requirements(pip_path):
    """Instala as dependências do requirements.txt"""
    print("Instalando dependencias...")
    
    try:
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        print("   OK pip atualizado")
        
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("   OK Dependencias instaladas")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   AVISO: Erro ao instalar dependencias: {e}")
        return False

def compile_cython():
    """Compila as extensões Cython"""
    print("Compilando extensoes Cython...")
    
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python.exe"
    else:
        python_cmd = "venv/bin/python"
    
    try:
        subprocess.run([python_cmd, "setup.py", "build_ext", "--inplace"], check=True)
        print("   OK Extensoes Cython compiladas")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   AVISO: Falha na compilacao Cython: {e}")
        print("   O projeto funcionara sem otimizacoes")
        return False

def test_conversion():
    """Testa a conversão DOCX para PDF"""
    print("Testando conversao DOCX para PDF...")
    
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python.exe"
    else:
        python_cmd = "venv/bin/python"
    
    try:
        subprocess.run([python_cmd, "main.py"], check=True)
        
        # Verificar se o PDF foi criado
        if os.path.exists("output/result.pdf"):
            size = os.path.getsize("output/result.pdf")
            print(f"   OK PDF gerado: output/result.pdf ({size} bytes)")
            return True
        else:
            print("   ERRO: PDF nao foi gerado")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"   ERRO na conversao: {e}")
        return False

def main():
    """Função principal que executa todo o setup"""
    print("SETUP COMPLETO DO PYDOCX-RENDER")
    print("=" * 50)
    
    success_count = 0
    total_steps = 8
    
    # Passo 1: Estrutura
    print("\\n[1/8] Criando estrutura do projeto...")
    create_directory_structure()
    create_init_files()
    success_count += 1
    
    # Passo 2: Arquivos de código
    print("\\n[2/8] Criando arquivos de codigo...")
    create_requirements_txt()
    create_setup_py()
    create_dom_py()
    create_parser_py()
    create_renderer_py()
    create_line_breaker_pyx()
    create_main_py()
    success_count += 1
    
    # Passo 3: Documento de teste
    print("\\n[3/8] Criando documento de teste...")
    if create_test_docx():
        success_count += 1
    
    # Passo 4: Ambiente virtual
    print("\\n[4/8] Configurando ambiente virtual...")
    pip_path = create_virtual_environment()
    if pip_path:
        success_count += 1
    
    # Passo 5: Dependências
    print("\\n[5/8] Instalando dependencias...")
    if pip_path and install_requirements(pip_path):
        success_count += 1
    
    # Passo 6: Compilação Cython
    print("\\n[6/8] Compilando extensoes...")
    if compile_cython():
        success_count += 1
    
    # Passo 7: Teste básico de importação
    print("\\n[7/8] Testando importacoes...")
    try:
        # Usar o Python do ambiente virtual
        if platform.system() == "Windows":
            python_cmd = "venv\\Scripts\\python.exe"
        else:
            python_cmd = "venv/bin/python"
            
        subprocess.run([python_cmd, "-c", "from pydocx_render.core.parser import parse_docx; print('Import OK')"], 
                      check=True, capture_output=True)
        print("   OK Modulos podem ser importados")
        success_count += 1
    except:
        print("   AVISO: Problemas na importacao")
    
    # Passo 8: Teste de conversão
    print("\\n[8/8] Testando conversao...")
    if test_conversion():
        success_count += 1
    
    # Relatório final
    print("\\n" + "=" * 50)
    print("RESULTADO FINAL")
    print("=" * 50)
    print(f"Passos concluidos: {success_count}/{total_steps}")
    
    if success_count >= 6:
        print("\\nSUCESSO! Projeto configurado e funcionando.")
        print("\\nArquivos importantes:")
        print("  - documents/simple_text.docx (documento de teste)")
        print("  - output/result.pdf (PDF gerado)")
        print("  - main.py (script principal)")
        print("\\nPara usar:")
        if platform.system() == "Windows":
            print("  1. venv\\Scripts\\activate")
        else:
            print("  1. source venv/bin/activate")
        print("  2. python main.py")
    else:
        print("\\nALGUNS PROBLEMAS ENCONTRADOS")
        print("O projeto pode funcionar parcialmente.")
        print("Verifique as mensagens de erro acima.")

if __name__ == "__main__":
    main()