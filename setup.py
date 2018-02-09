from distutils.core import setup

setup(
    name='factoryboy-gaendb',
    version='0.1.6',
    packages=[
        'gaendb',
    ],
    license='Apache v2',
    long_description=open('pypi.rst').read(),
    description='Factoryboy base factories and helpers for Google App Engine ndb models',
    author="Anentropic",
    author_email="ego@anentropic.com",
    url="https://github.com/anentropic/factoryboy-gaendb",
    install_requires=[
        "factory_boy",
    ],
)
