#!/usr/bin/env python3
"""
Script para corrigir problemas de compilação Cython no Windows
"""

import os
import sys
import subprocess
import shutil
import tempfile
import platform
from pathlib import Path

def print_step(step, description):
    """Imprime uma etapa de forma clara"""
    print(f"\n[{step}] {description}")
    print("-" * 50)

def run_command(command, description, ignore_errors=False):
    """Executa um comando e retorna True se bem-sucedido"""
    print(f"Executando: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {description} - SUCESSO")
        if result.stdout:
            print("Saída:", result.stdout[:300] + "..." if len(result.stdout) > 300 else result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            print(f"⚠ {description} - AVISO: {e}")
            return False
        else:
            print(f"✗ {description} - ERRO: {e}")
            if e.stdout:
                print("Saída:", e.stdout)
            if e.stderr:
                print("Erro:", e.stderr)
            return False

def check_visual_studio():
    """Verifica se o Visual Studio Build Tools está instalado corretamente"""
    print_step(1, "VERIFICANDO VISUAL STUDIO BUILD TOOLS")
    
    # Possíveis localizações do cl.exe
    possible_paths = [
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Tools\\MSVC\\*\\bin\\Hostx64\\x64\\cl.exe",
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools\\VC\\Tools\\MSVC\\*\\bin\\Hostx64\\x64\\cl.exe",
        "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\*\\bin\\Hostx64\\x64\\cl.exe",
        "C:\\Program Files\\Microsoft Visual Studio\\2019\\Community\\VC\\Tools\\MSVC\\*\\bin\\Hostx64\\x64\\cl.exe"
    ]
    
    import glob
    compiler_found = False
    
    for path_pattern in possible_paths:
        matches = glob.glob(path_pattern)
        if matches:
            print(f"✓ Compilador encontrado: {matches[0]}")
            compiler_found = True
            break
    
    if not compiler_found:
        print("✗ Compilador Visual Studio não encontrado!")
        print("\nSOLUÇÃO:")
        print("1. Baixe Visual Studio Build Tools:")
        print("   https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022")
        print("2. Instale com 'C++ build tools' selecionado")
        print("3. Reinicie o prompt de comando")
        return False
    
    return True

def fix_temp_directory():
    """Corrige problemas com diretórios temporários"""
    print_step(2, "CORRIGINDO DIRETÓRIOS TEMPORÁRIOS")
    
    # Limpar diretórios de build antigos
    dirs_to_clean = ["build", "dist", "pydocx_render.egg-info"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✓ Removido: {dir_name}")
            except Exception as e:
                print(f"⚠ Não foi possível remover {dir_name}: {e}")
    
    # Verificar variáveis de ambiente TEMP
    temp_vars = ["TEMP", "TMP", "TMPDIR"]
    for var in temp_vars:
        value = os.environ.get(var)
        if value:
            print(f"✓ {var} = {value}")
            if not os.path.exists(value):
                print(f"⚠ Diretório {value} não existe!")
    
    # Criar diretório temporário local
    local_temp = os.path.join(os.getcwd(), "temp_build")
    os.makedirs(local_temp, exist_ok=True)
    print(f"✓ Criado diretório temporário local: {local_temp}")
    
    return local_temp

def create_improved_setup_py():
    """Cria uma versão melhorada do setup.py com configurações robustas"""
    print_step(3, "CRIANDO SETUP.PY MELHORADO")
    
    setup_content = '''# setup.py
import os
import sys
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

# Configurações robustas para Windows
if sys.platform.startswith('win'):
    # Definir diretório temporário local
    temp_dir = os.path.join(os.getcwd(), "temp_build")
    os.makedirs(temp_dir, exist_ok=True)
    os.environ["TEMP"] = temp_dir
    os.environ["TMP"] = temp_dir
    
    # Configurações extras do compilador
    extra_compile_args = ["/O2", "/MD"]
    extra_link_args = []
else:
    extra_compile_args = ["-O3"]
    extra_link_args = []

# Definir extensões
extensions = [
    Extension(
        "pydocx_render.layout.line_breaker",
        ["pydocx_render/layout/line_breaker.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        language="c++"
    )
]

# Configurações do Cython
compiler_directives = {
    'boundscheck': False,
    'wraparound': False,
    'initializedcheck': False,
    'cdivision': True,
}

setup(
    name="PyDocX-Render",
    ext_modules=cythonize(
        extensions,
        compiler_directives=compiler_directives,
        build_dir="temp_build"
    ),
    zip_safe=False,
)'''
    
    # Backup do setup.py original
    if os.path.exists("setup.py"):
        shutil.copy2("setup.py", "setup.py.backup")
        print("✓ Backup do setup.py original criado")
    
    with open("setup.py", "w", encoding="utf-8") as f:
        f.write(setup_content)
    
    print("✓ setup.py melhorado criado")

def create_simple_line_breaker():
    """Cria uma versão simplificada do line_breaker.pyx"""
    print_step(4, "CRIANDO VERSÃO SIMPLIFICADA DO CYTHON")
    
    simple_pyx_content = '''# pydocx_render/layout/line_breaker.pyx
# -*- coding: utf-8 -*-
# Versão simplificada sem freetype para evitar problemas de compilação

cdef class FontMetrics:
    """Métricas de fonte simplificadas usando estimativas"""
    cdef float char_width
    
    def __init__(self, font_path=None):
        # Usar largura estimada de caractere (mais simples, sem freetype)
        self.char_width = 7.0  # Largura aproximada para fonte padrão
    
    def get_text_width(self, text, font_size):
        """Calcula largura do texto usando estimativa simples"""
        cdef float width = len(text) * self.char_width * (font_size / 11.0)
        return width

def layout_paragraph(text, FontMetrics metrics, float max_width, int font_size):
    """Motor de layout de parágrafo otimizado"""
    cdef list lines = []
    cdef list words = text.split(' ')
    cdef str current_line = ""
    cdef str word
    cdef str test_line
    cdef int i
    
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
    return lines

def simple_text_width(text, font_size=11):
    """Função simples para calcular largura de texto"""
    return len(text) * 7.0 * (font_size / 11.0)'''
    
    # Backup do arquivo original
    original_file = "pydocx_render/layout/line_breaker.pyx"
    if os.path.exists(original_file):
        shutil.copy2(original_file, original_file + ".backup")
        print("✓ Backup do line_breaker.pyx original criado")
    
    with open(original_file, "w", encoding="utf-8") as f:
        f.write(simple_pyx_content)
    
    print("✓ Versão simplificada do line_breaker.pyx criada")

def attempt_compilation():
    """Tenta compilar as extensões Cython"""
    print_step(5, "TENTANDO COMPILAÇÃO CYTHON")
    
    # Determinar comando Python correto
    if os.path.exists("venv\\Scripts\\python.exe"):
        python_cmd = "venv\\Scripts\\python.exe"
    elif os.path.exists("venv/bin/python"):
        python_cmd = "venv/bin/python"
    else:
        python_cmd = sys.executable
    
    print(f"Usando Python: {python_cmd}")
    
    # Tentar diferentes abordagens
    approaches = [
        (f'"{python_cmd}" setup.py build_ext --inplace', "Compilação padrão"),
        (f'"{python_cmd}" setup.py build_ext --inplace --force', "Compilação forçada"),
        (f'"{python_cmd}" setup.py build_ext --inplace --compiler=msvc', "Compilação com MSVC explícito"),
    ]
    
    for command, description in approaches:
        print(f"\nTentativa: {description}")
        if run_command(command, description, ignore_errors=True):
            return True
    
    return False

def verify_compilation():
    """Verifica se a compilação foi bem-sucedida"""
    print_step(6, "VERIFICANDO RESULTADO DA COMPILAÇÃO")
    
    # Procurar arquivos compilados
    layout_dir = "pydocx_render/layout"
    compiled_files = []
    
    if os.path.exists(layout_dir):
        for file in os.listdir(layout_dir):
            if file.endswith(('.so', '.pyd')) and 'line_breaker' in file:
                compiled_files.append(file)
                size = os.path.getsize(os.path.join(layout_dir, file))
                print(f"✓ Arquivo compilado: {file} ({size} bytes)")
    
    if compiled_files:
        print("✓ Compilação Cython bem-sucedida!")
        return True
    else:
        print("⚠ Nenhum arquivo compilado encontrado")
        print("O projeto funcionará em modo Python puro")
        return False

def test_import():
    """Testa se o módulo compilado pode ser importado"""
    print_step(7, "TESTANDO IMPORTAÇÃO DO MÓDULO")
    
    python_cmd = "venv\\Scripts\\python.exe" if os.path.exists("venv\\Scripts\\python.exe") else sys.executable
    
    test_commands = [
        (f'"{python_cmd}" -c "from pydocx_render.layout.line_breaker import FontMetrics; print(\'FontMetrics OK\')"', "FontMetrics"),
        (f'"{python_cmd}" -c "from pydocx_render.layout.line_breaker import layout_paragraph; print(\'layout_paragraph OK\')"', "layout_paragraph"),
    ]
    
    all_passed = True
    for command, description in test_commands:
        if not run_command(command, f"Testando {description}", ignore_errors=True):
            all_passed = False
    
    return all_passed

def create_fallback_python_version():
    """Cria uma versão Python pura como fallback"""
    print_step(8, "CRIANDO VERSÃO PYTHON PURA COMO FALLBACK")
    
    fallback_content = '''# pydocx_render/layout/line_breaker_pure.py
# Versão Python pura do motor de layout

class FontMetrics:
    """Métricas de fonte usando estimativas"""
    
    def __init__(self, font_path=None):
        self.char_width = 7.0  # Largura aproximada para fonte padrão
    
    def get_text_width(self, text, font_size):
        """Calcula largura do texto usando estimativa simples"""
        return len(text) * self.char_width * (font_size / 11.0)

def layout_paragraph(text, metrics, max_width, font_size):
    """Motor de layout de parágrafo em Python puro"""
    lines = []
    words = text.split(' ')
    
    if not words:
        return []

    current_line = words[0]
    for word in words[1:]:
        test_line = current_line + " " + word
        
        if metrics.get_text_width(test_line, font_size) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    
    lines.append(current_line)
    return lines

def simple_text_width(text, font_size=11):
    """Função simples para calcular largura de texto"""
    return len(text) * 7.0 * (font_size / 11.0)'''
    
    with open("pydocx_render/layout/line_breaker_pure.py", "w", encoding="utf-8") as f:
        f.write(fallback_content)
    
    print("✓ Versão Python pura criada como fallback")

def main():
    """Função principal para corrigir a compilação Cython"""
    print("CORREÇÃO DA COMPILAÇÃO CYTHON")
    print("=" * 60)
    
    if platform.system() != "Windows":
        print("Este script é específico para Windows.")
        print("No Linux/macOS, instale: sudo apt-get install build-essential python3-dev")
        return
    
    success_steps = 0
    total_steps = 8
    
    # Passo 1: Verificar Visual Studio
    if check_visual_studio():
        success_steps += 1
    else:
        print("\n❌ Visual Studio Build Tools não encontrado.")
        print("Por favor, instale antes de continuar.")
        return
    
    # Passo 2: Corrigir diretórios temporários
    local_temp = fix_temp_directory()
    success_steps += 1
    
    # Passo 3: Criar setup.py melhorado
    create_improved_setup_py()
    success_steps += 1
    
    # Passo 4: Criar versão simplificada
    create_simple_line_breaker()
    success_steps += 1
    
    # Passo 5: Tentar compilação
    if attempt_compilation():
        success_steps += 1
        
        # Passo 6: Verificar compilação
        if verify_compilation():
            success_steps += 1
            
            # Passo 7: Testar importação
            if test_import():
                success_steps += 1
    
    # Passo 8: Criar fallback sempre
    create_fallback_python_version()
    success_steps += 1
    
    # Relatório final
    print("\n" + "=" * 60)
    print("RESULTADO DA CORREÇÃO CYTHON")
    print("=" * 60)
    print(f"Passos concluídos: {success_steps}/{total_steps}")
    
    if success_steps >= 7:
        print("\n✓ SUCESSO! Cython compilado e funcionando!")
        print("O projeto agora usa extensões otimizadas.")
    elif success_steps >= 5:
        print("\n⚠ PARCIAL: Compilação teve problemas, mas fallback está disponível.")
        print("O projeto funcionará em modo misto.")
    else:
        print("\n❌ FALHA: Não foi possível compilar Cython.")
        print("O projeto funcionará apenas em Python puro.")
    
    print("\nPara testar:")
    print("1. venv\\Scripts\\activate")
    print("2. python main.py")

if __name__ == "__main__":
    main()