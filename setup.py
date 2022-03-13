from setuptools import setup

setup(
    install_requires=[
        'python-ldap'
    ],
    extras_require={
        'dev': [
            'build',
            'ipython',
            'prompt-toolkit',
            'pylint',
            'twine',
        ]
    },
)
