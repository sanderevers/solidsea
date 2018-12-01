"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from solidsea import __version__

setup(
    name='solidsea',
    version=__version__,
    description='A stateless OIDC federation server.',
    author='Sander Evers',
    packages=find_packages(),
    install_requires=['Flask==1.0.2','Authlib==0.10','requests==2.20.0'],
    entry_points={},
    url = 'https://github.com/sanderevers/solidsea',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3.6',
    ],
    package_data={
        '': ['templates/*'],
    },
)