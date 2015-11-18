from setuptools import setup


setup(
    name='alexandra',
    version='0.0.0',
    description='Toolkit for writing Amazon Alexa skills as web services',
    author='Erik Price',
    url='https://github.com/erik/alexandra',
    packages=['alexandra'],
    license='ISC',
    install_requires=open('requirements.txt').readlines()
)
