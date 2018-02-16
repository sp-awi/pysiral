from Cython.Build import cythonize
from setuptools.extension import Extension
from setuptools import setup
import numpy
import os

extensions = [
    Extension("pysiral.bnfunc.cytfmra", [os.path.join("pysiral", "bnfunc", "cytfmra.pyx")])]

setup(
    name = "cysiral",
    version = "0.1",
    author = "Stefan Hendricks",
    author_email = "stefan.hendricks@awi.de",
    ext_modules = cythonize(extensions),
    include_dirs = [numpy.get_include()]
)