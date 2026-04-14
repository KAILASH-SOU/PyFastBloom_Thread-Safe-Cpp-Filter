from setuptools import setup, Extension
import pybind11

functions_module = Extension(
    'fastbloom',
    sources=['bindings.cpp'],
    include_dirs=[pybind11.get_include()],
    language='c++',
    extra_compile_args=['-std=c++17'],
)

setup(
    name='fastbloom',
    version='0.1.0',
    description='A fast, thread-safe Bloom Filter native extension.',
    ext_modules=[functions_module],
    zip_safe=False,
)
