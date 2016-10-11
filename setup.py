# -*- coding: utf-8 -*-

from setuptools import setup
import platform


requires = ['psutil>=4.3.1']

if platform.system() == 'Windows':
    requires.append('pypiwin32')


setup(
    name='screen-god',
    version='0.0.1',
    description='Manage windows and their position on the screen',
    url='https://github.com/kyzima-spb/screen-god',
    license='Apache License 2.0',
    author='Kirill Vercetti',
    author_email='office@kyzima-spb.com',
    packages=['screen_god'],
    install_requires=requires,
    scripts=[],
    py_modules=[],
)
