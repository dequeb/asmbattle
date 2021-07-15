"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py build_ext --inplace
    python setup.py bdist bdist_wheel py2app
"""

from setuptools import setup
from Cython.Build import cythonize
from Cython.Distutils import build_ext


setup(
    name='asmbattle',
    version='0.9.1',
    author='Michel Rondeau',
    author_email='mr@michelrondeau.com',
    url='https:://www.asmblattle.com',
    description='simple assembler code training and game',
    long_description=open("README.md").read(),
    # packages = ['asmbattle'],
    classifiers=[
        'Development Status :: 2 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9'
    ],
    # Include additional files into the package using MANIFEST.in
    include_package_data=True,
    app= ['asmbattle/__main__.py'],
    # data_files=["./locale/*", "./ASM/*"],
    package_data={'locale': ['*.mo', '*.po', '*.pot'],
                  'ASM': ['*.asm']},
    cmdclass = {'build_ext': build_ext},
    ext_modules = cythonize(["asmbattle/opcodes.pyx",
                             "asmbattle/assembler.pyx",
                             "asmbattle/cpu.pyx",
                             "asmbattle/memory.pyx",
                             "asmbattle/ui_controller.pyx",
                             "asmbattle/ui_view.pyx",
                             "asmbattle/aboutbox.pyx"], language_level=3),

    keywords='assembler programing game',
    setup_requires=['py2app'],
    options={'py2app': {'iconfile': "resources/asmbattle.icns"},
             'cython': {"language_level":"3"}},
    install_requires=[
        "Cython", "PyQt6", "pygubu", "pillow", "markdown", "tk_html_widgets"
    ],
    entry_points={
        "gui_scripts": [
            "asmbattle = __main__:main"
        ]
    },
)
