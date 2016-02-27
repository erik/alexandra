from setuptools import setup

setup(
    name='alexandra',
    version='0.2.0',
    description='Toolkit for writing Amazon Alexa skills as web services',
    author='Erik Price',
    url='https://github.com/erik/alexandra',
    packages=['alexandra'],
    license='ISC',
    test_requires=['tox'],
    install_requires=[
        'Werkzeug==0.11.4',
        'pyOpenssl==0.15.1'
    ]
)
