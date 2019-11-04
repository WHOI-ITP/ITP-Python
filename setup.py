from setuptools import setup


setup(
    name='itp_python',
    version='0.0.2',
    url='https://github.com/WHOI-ITP/ITP-Python',
    author='Jeff Grant',
    author_email='jeffery.grant@gmail.com',
    description='Python software for accessing and manipulating Ice '
                'Tethered Profiler data',
    packages=['itp_python', ],
    install_requires=[
        'h5py',
        'numpy',
        'gsw',
        'pytest',
        'pytest-cov',
        'pytest-mock']
)