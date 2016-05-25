import os

from setuptools import setup, find_packages

__version__ = '0.3'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='pylock',
    version=__version__,
    description='Python Distributed Lock',
    long_description=README,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
    ],
    keywords='lock redis',
    author="Nathan Duthoit",
    author_email="nathan@waveapps.com",
    url="http://github.com/waveaccounting/pylock",
    license="BSD",
    packages=find_packages(),
    test_suite="pylock.tests",
    include_package_data=True,
    zip_safe=False,
    tests_require=['Mock>=2.0.0', 'nose'],
    install_requires=[
        "redis>=2.6.1",
    ]
)
