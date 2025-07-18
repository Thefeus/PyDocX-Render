# setup.py
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
)