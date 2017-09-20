#!/usr/bin/env python
"""s2reader setup configuration."""

from setuptools import setup

setup(
    name='s2reader',
    version='0.4',
    description='simple metadata reader for Sentinel-2 SAFE files',
    author='Joachim Ungar',
    author_email='joachim.ungar@gmail.com',
    url='https://github.com/ungarj/s2reader',
    license='MIT',
    packages=[  # TODO fix module structure
        's2reader', 's2reader.cli'
    ],
    entry_points={
        'console_scripts': [
            's2_inspect = s2reader.cli.inspect:main',
            's2_transform = s2reader.cli.transform:main'
        ],
    },
    install_requires=[
        'lxml',
        'shapely',
        'numpy',
        'pyproj',
        'cached_property',
        'zipfile2',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: GIS',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
