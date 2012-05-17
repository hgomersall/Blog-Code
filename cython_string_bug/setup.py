
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [
        Extension(
            'string_test', ['string_test.pyx'],
            include_dirs=['hello_string'],
            libraries=['hello_string'],
            library_dirs=['.'])]
)

