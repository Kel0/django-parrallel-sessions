from setuptools import setup

setup(
    name="dps",
    version='0.1',
    py_modules=['dps.cli'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'dps = dps.cli:run'
        ]
    },
)
