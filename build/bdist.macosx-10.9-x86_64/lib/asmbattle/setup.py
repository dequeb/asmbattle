'''
Created on 3 janv. 2018

@author: michel
'''
from distutils.core import setup

setup(
    name='asmbattle',
    version='0.01',     # development in progress
    author='Michel Rondeau',
    author_email = 'mr@michelrondeau.com',
    url='https:://www.michelrondeau.com/asmblattle',
    description='simple assembler code battle in virtual machine',
    long_description='''Assembler programs are developped and test 
    and run against another for the control of the machine.''',
    packages = ['.'],
    classifiers=[
        'Development Status :: 0 - Developpment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9'
        ],
    keywords='assembler programing game',
    #  entry_points={
    #    'console_scripts': [
    #        'convert=multiconfig:main'
    #      ]
    #  }
)