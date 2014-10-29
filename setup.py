from distutils.core import setup

setup(
    name='factoryboy-gaendb',
    version='0.1.0',
    packages=[
        'gaendb',
    ],
    license='Apache v2',
    long_description=open('pypi.rst').read(),
    author="Anentropic",
    author_email="ego@anentropic.com",
    url="https://github.com/anentropic/factoryboy-gaendb",
    install_requires=[
        "google-appengine",
        "factory_boy",
    ],
)
