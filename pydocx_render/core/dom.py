# pydocx_render/core/dom.py
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
    body: List[Paragraph] = field(default_factory=list)