import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='itpwhoi',
    version='0.0.3',
    author='Jeff Grant',
    author_email='jeffery.grant@gmail.com',
    description='A package for querying Ice Tethered Profiler data',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://www2.whoi.edu/site/itp/',
    project_urls={
        'Bug Tracker': 'https://github.com/WHOI-ITP/ITP-Python/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=['itp'],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'gsw@git+https://github.com/TEOS-10/python-gsw@master'
    ],
    extras_require={
        'testing':
        ['flake8', 'pytest', 'pytest-cov']
    }
)
