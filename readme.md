# PyDocX-Render

**Versão:** 0.1.0
**Status:** Núcleo funcional

`PyDocX-Render` é um SDK (Software Development Kit) desenvolvido em Python, projetado para converter documentos `.docx` em arquivos PDF com alta fidelidade. O projeto utiliza Cython para compilar as partes críticas de performance (como o motor de layout de texto) para código C nativo, garantindo velocidade e eficiência.

## Funcionalidades Atuais

- **Parsing de DOCX:** Lê a estrutura de documentos `.docx`, extraindo parágrafos e trechos de texto (`runs`).
- **Suporte a Estilos Básicos:** Reconhece e renderiza formatação de **negrito** e *itálico*.
- **Motor de Layout Otimizado:**
  - Realiza a quebra de linha de parágrafos para que o texto se ajuste às margens da página.
  - Lida com parágrafos que contêm múltiplos estilos (negrito/itálico) na mesma linha.
  - Otimizado com **Cython** para alta performance.
- **Renderização em PDF:** Gera um arquivo PDF a partir da estrutura do documento analisado.

## Como Usar

### Pré-requisitos

1.  **Python 3.9+**
2.  **Microsoft C++ Build Tools (Apenas para Windows):** O Cython precisa de um compilador C++.
    -   Baixe o instalador do [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022).
    -   Durante a instalação, selecione a carga de trabalho **"Desenvolvimento para desktop com C++"**.

### Instalação e Execução

O projeto inclui scripts para automatizar todo o processo de configuração.

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd pydocx-render
    ```

2.  **Execute o script de setup completo:**
    Este script irá criar a estrutura de pastas, o ambiente virtual, instalar as dependências e compilar o código Cython.
    ```bash
    python setup_project.py
    ```
    O script é autoguiado e mostrará o progresso de cada etapa.

3.  **Execute a conversão:**
    Após o setup bem-sucedido, ative o ambiente virtual e execute o programa principal.

    - **No Windows:**
      ```bash
      venv\Scripts\activate
      python main.py
      ```

    - **No Linux / macOS:**
      ```bash
      source venv/bin/activate
      python main.py
      ```

4.  **Verifique o resultado:**
    - O documento de teste `documents/simple_text.docx` será convertido.
    - O resultado será salvo em `output/result.pdf`.

### Solução de Problemas (Troubleshooting)

Se a compilação do Cython falhar durante o `setup_project.py`, você pode usar o script de diagnóstico `fix_cython.py`.

```bash
python fix_cython.py