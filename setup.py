"""

Usage:
    python setup.py bdist_wheel py2app
"""

from setuptools import setup
import os
if os.name == 'nt':
    import py2exe

setup(
    #  ####################
    #  documentation
    #  ####################
    name='asmbattle',
    version='0.9.1',
    author='Michel Rondeau',
    author_email='mr@michelrondeau.com',
    url='https:://www.michelrondea.com/asmbattle',
    description='simple assembler code training and game',
    long_description=open("README.md").read(),
    classifiers=[
        'Development Status :: 2 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9'
    ],
    keywords='assembler programing game',

    #  ####################
    #  data files
    #  ####################
    package_data={'locale': ['locale/*'],
                  'ASM': ['ASM/*'],
                  'resources' : ['resources/*']},
    data_files=[('doc', ['CHANGELOG.md', 'CHANGELOG_fr.MD', 'VERSION']),],
    include_package_data=True,

    #  ####################
    #  build instructions
    #  ####################
    packages = ['asmbattle'],
    app= ['asmbattle/__main__.py'],
    setup_requires=['py2app', 'py2exe'],
    options={'py2app': {'iconfile': "resources/asmbattle.icns"}},
    install_requires=["pillow", "markdown2", "tk_html_widgets", "wheel"],
    entry_points={
        "gui_scripts": [
            "asmbattle = __main__:main"
        ]
    },
)
