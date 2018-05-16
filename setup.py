from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'VERSION')) as version_file:
    version = version_file.read().strip()

setup(
    name='compiledb',
    version=version,
    description='Tool for generating LLVM Compilation Database files for make-based build systems.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nickdiego/compiledb-generator',
    author='Nick Yamane',
    author_email='nick@diegoyam.com',
    license='GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='compilation-database clang c cpp makefile rtags completion',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[],
    extras_require={
        'dev': [],
        'test': ['pytest'],
    },
    python_requires='>=2.7',
    entry_points={
        'console_scripts': [
            'compiledb=compiledb:cli',
        ],
    },
    project_urls={
        'Issue Tracking': 'https://github.com/nickdiego/compiledb-generator/issues',
        # 'Funding': 'https://donate.pypi.org',
        # 'Samples': 'https://github.com/nickdiego/compiledb-generator/samples',
    },
)

