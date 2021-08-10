from setuptools import setup

setup(
    install_requires=[
        'python-ldap >= 3.3.1'
    ],
    extras_require={
        'dev': [
            'build >= 0.6.0.post1',
            'ipython >= 7.18.1',
            'prompt-toolkit >= 3.0.8',
            'pylint >= 2.6.0',
            'twine >= 3.4.2',
        ]
    },
)