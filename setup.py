from setuptools import setup

setup(
    name='alexandra',
    version='0.3.2',
    description='Toolkit for writing Amazon Alexa skills as web services',
    author='Erik Price',
    url='https://github.com/erik/alexandra',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Home Automation',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    packages=['alexandra'],
    license='ISC',
    test_requires=['tox'],
    install_requires=[
        'Werkzeug==0.11.4',
        'pyOpenssl==16.2.0'
    ]
)
