from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

about = {}
with open(path.join(here, 'compiledb', '__version__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    license=about['__license__'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent'
    ],
    keywords='compilation-database clang c cpp makefile rtags completion',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'click',
        'bashlex'
    ],
    extras_require={
        'dev': [],
        'test': ['pytest'],
    },
    python_requires='>=2.7',
    entry_points={
        'console_scripts': [
            'compiledb=compiledb.cli:cli',
        ],
    },
    project_urls={
        'Issue Tracking': 'https://github.com/nickdiego/compiledb-generator/issues',
        # 'Funding': 'https://donate.pypi.org',
        # 'Samples': 'https://github.com/nickdiego/compiledb-generator/samples',
    },
)

