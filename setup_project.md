# PyDocX-Render - Guia de Instalação e Configuração

## 📋 Visão Geral

Este documento fornece instruções detalhadas para configurar o projeto PyDocX-Render, um renderizador de documentos DOCX para PDF desenvolvido em Python com Cython para alta performance.

## 🎯 Pré-requisitos

- **Python 3.8+** instalado no sistema
- **Git** (opcional, para controle de versão)
- **Visual Studio Build Tools** (Windows) ou **build-essential** (Linux) para compilação Cython
- **Conexão com internet** para download de dependências

### Verificação dos Pré-requisitos

```bash
# Verificar versão do Python
python --version

# Verificar se pip está disponível
pip --version
```

## 🚀 Instalação Automática

### Passo 1: Download dos Scripts de Setup

Baixe ou crie os seguintes arquivos no diretório do projeto:

1. **setup_project.py** - Script principal de configuração
2. **create_test_docx.py** - Script para criar documento de teste

### Passo 2: Executar o Setup Automático

```bash
# Execute o script de configuração
python setup_project.py
```

**Saída esperada:**
```
=== Setup do projeto PyDocX-Render ===

Criando estrutura de diretorios...
   OK documents/
   OK output/
   OK pydocx_render/
   ...
=== Setup concluido! ===
```

## 🔧 Configuração Manual (Pós-Setup)

### Passo 3: Ativar o Ambiente Virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Confirmação:** O prompt deve mostrar `(venv)` no início.

### Passo 4: Instalar Dependências

```bash
# Atualizar pip (se necessário)
python -m pip install --upgrade pip

# Instalar dependências do projeto
pip install -r requirements.txt

# Instalar dependência adicional para criar documentos de teste
pip install python-docx
```

### Passo 5: Criar Documento de Teste

```bash
# Gerar um documento DOCX de exemplo
python create_test_docx.py
```

**Resultado:** Arquivo `documents/simple_text.docx` será criado.

### Passo 6: Compilar Extensões Cython

```bash
# Compilar o motor de layout em Cython
python setup.py build_ext --inplace
```

**Saída esperada:**
```
Compiling pydocx_render/layout/line_breaker.pyx because it changed.
[1/1] Cythonizing pydocx_render/layout/line_breaker.pyx
building 'pydocx_render.layout.line_breaker' extension
...
```

### Passo 7: Executar o Projeto

```bash
# Converter DOCX para PDF
python main.py
```

**Saída esperada:**
```
Parsing 'documents/simple_text.docx'...
DOM criado com sucesso.
Rendering to 'output/result.pdf'...
PDF gerado com sucesso!
```

## 📁 Estrutura de Arquivos Criada

```
pydocx-render/
├── documents/                    # Documentos DOCX para teste
│   └── simple_text.docx         # Documento de exemplo
├── output/                       # PDFs gerados
│   └── result.pdf               # PDF de saída
├── pydocx_render/               # Código principal
│   ├── __init__.py
│   ├── core/                    # Parser e DOM
│   │   ├── __init__.py
│   │   ├── dom.py              # Modelo de dados
│   │   └── parser.py           # Parser DOCX
│   ├── layout/                  # Motor de layout
│   │   ├── __init__.py
│   │   └── line_breaker.pyx    # Layout engine (Cython)
│   └── renderer.py             # Renderizador PDF
├── tests/                       # Testes (futuro)
├── venv/                        # Ambiente virtual
├── main.py                      # Ponto de entrada
├── setup.py                     # Configuração Cython
├── requirements.txt             # Dependências
└── README.md                    # Documentação básica
```

## 🔍 Verificação da Instalação

### Teste Básico

1. **Verificar se o ambiente virtual está ativo:**
   ```bash
   which python  # Linux/macOS
   where python  # Windows
   ```

2. **Verificar se as dependências estão instaladas:**
   ```bash
   pip list
   ```

3. **Testar importação dos módulos:**
   ```bash
   python -c "from pydocx_render.core.parser import parse_docx; print('Parser OK')"
   python -c "from pydocx_render.renderer import render_to_pdf; print('Renderer OK')"
   ```

### Teste de Conversão

```bash
# Teste completo de conversão
python main.py
```

**Arquivos gerados:**
- `output/result.pdf` - PDF convertido
- Sem erros no console

## ⚠️ Solução de Problemas

### Problema 1: Erro de Compilação Cython

**Sintomas:**
```
error: Microsoft Visual C++ 14.0 is required
```

**Solução Windows:**
1. Instalar [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)
2. Ou instalar [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

**Solução Linux:**
```bash
sudo apt-get install build-essential python3-dev
```

### Problema 2: Erro no freetype-py

**Sintomas:**
```
ImportError: No module named 'freetype'
```

**Solução temporária:**
- O projeto funcionará sem o motor de layout avançado
- Para corrigir: instalar FreeType development headers

**Windows:**
```bash
pip install freetype-py --no-cache-dir
```

**Linux:**
```bash
sudo apt-get install libfreetype6-dev
pip install freetype-py
```

### Problema 3: Arquivo DOCX não encontrado

**Sintomas:**
```
FileNotFoundError: documents/simple_text.docx
```

**Soluções:**
1. **Executar o gerador de teste:**
   ```bash
   python create_test_docx.py
   ```

2. **Ou usar arquivo existente:**
   - Copiar qualquer arquivo .docx para `documents/simple_text.docx`

3. **Ou modificar o main.py:**
   ```python
   input_file = "caminho/para/seu/arquivo.docx"
   ```

### Problema 4: Erro de Codificação (Windows)

**Sintomas:**
```
UnicodeEncodeError: 'charmap' codec can't encode
```

**Solução:**
```bash
# Definir codificação UTF-8
set PYTHONIOENCODING=utf-8
python main.py
```

## 🚀 Próximos Passos de Desenvolvimento

### Funcionalidades a Implementar

1. **Suporte a estilos avançados**
   - Tamanhos de fonte variáveis
   - Cores de texto
   - Alinhamento de parágrafos

2. **Suporte a elementos complexos**
   - Tabelas
   - Imagens
   - Listas numeradas/com marcadores

3. **Melhorias de layout**
   - Quebra de página automática
   - Margens configuráveis
   - Cabeçalhos e rodapés

### Estrutura de Testes

```bash
# Criar testes unitários
mkdir tests/unit tests/integration

# Executar testes (futuro)
python -m pytest tests/
```

### Performance e Otimização

1. **Profiling do código:**
   ```bash
   python -m cProfile main.py
   ```

2. **Otimização Cython:**
   - Expandir uso de tipos estáticos
   - Otimizar loops críticos

## 📚 Recursos Adicionais

### Documentação das Dependências

- **lxml:** [https://lxml.de/](https://lxml.de/)
- **PyMuPDF:** [https://pymupdf.readthedocs.io/](https://pymupdf.readthedocs.io/)
- **Cython:** [https://cython.org/](https://cython.org/)
- **Pillow:** [https://pillow.readthedocs.io/](https://pillow.readthedocs.io/)

### Comandos Úteis

```bash
# Desativar ambiente virtual
deactivate

# Recompilar apenas extensões Cython
python setup.py build_ext --inplace --force

# Limpar arquivos compilados
python setup.py clean --all

# Listar dependências instaladas
pip freeze > requirements_freeze.txt
```

## 📝 Checklist de Instalação

- [ ] Python 3.8+ instalado
- [ ] Scripts de setup baixados
- [ ] `python setup_project.py` executado com sucesso
- [ ] Ambiente virtual ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Documento de teste criado (`python create_test_docx.py`)
- [ ] Extensões Cython compiladas (`python setup.py build_ext --inplace`)
- [ ] Teste de conversão executado (`python main.py`)
- [ ] PDF gerado em `output/result.pdf`

## 🎉 Conclusão

Após seguir todos os passos, você terá:

1. **Ambiente de desenvolvimento** configurado e funcional
2. **Projeto PyDocX-Render** executando conversões básicas
3. **Base sólida** para implementar funcionalidades avançadas
4. **Estrutura modular** preparada para expansão

O projeto está pronto para desenvolvimento iterativo seguindo a filosofia "Faça funcionar, depois faça certo, depois faça rápido".