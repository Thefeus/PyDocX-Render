# main.py
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
    main()