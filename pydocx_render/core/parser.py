# pydocx_render/core/parser.py
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

    return doc